"""Volumetric thermal expansion coefficient via the Debye-Grüneisen approximation."""
from typing import Dict
import numpy as np
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure

# numpy 2.0 renamed trapz -> trapezoid (trapz is removed in numpy >= 2.0).
_trapz = getattr(np, "trapezoid", None) or np.trapz


def _debye_Cv(T_array, Theta_D, R=8.314):
    """Molar heat capacity (J/mol/K) at each temperature in T_array, Debye model."""
    Cv = np.zeros_like(T_array)
    with np.errstate(over="ignore"):
        for i, T in enumerate(T_array):
            x_max = Theta_D / T
            x = np.linspace(0.001, x_max, 1000)
            y = x**4 / (4 * np.sinh(x / 2) ** 2)  # == x^4*e^x / (e^x-1)^2, overflow-safe
            integral = _trapz(y, x)
            Cv[i] = 9 * R * (T / Theta_D) ** 3 * integral
    return Cv


@register
class ThermalExpansionCalculator(BaseCalculator):
    name = "Thermal Expansion Coefficient (Debye-Grüneisen)"
    description = (
        "Estimates the volumetric thermal expansion coefficient α(T) from the Grüneisen "
        "relation α = γ·Cv / (3·B·V_molar), using the Debye model for Cv(T). This is an "
        "order-of-magnitude approximation (constant γ, isotropic solid) — it is meant for "
        "quick sanity-checking against experiment, not as a precision prediction."
    )
    required_inputs = ["Theta_D", "B", "M", "rho", "gamma"]
    # Example for Silicon. Real Si alpha(300K) is ~2.6e-6 /K; the Debye-Gruneisen
    # estimate below is only accurate to within roughly a factor of ~2 for Si, because
    # Si's Gruneisen parameter is not actually constant with T (it is even negative
    # at very low T) -- this is a known limitation of the simple model, not a bug.
    example_inputs = {"Theta_D": 645.0, "B": 99.0, "M": 28.085, "rho": 2.33, "gamma": 1.0}
    expected_summary = "alpha(300K) ~ a few x 1e-6 /K (order-of-magnitude; real Si is ~2.6e-6 /K)."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        Theta_D, B_GPa, M, rho, gamma = p["Theta_D"], p["B"], p["M"], p["rho"], p["gamma"]

        if Theta_D <= 0:
            raise ValueError("Debye temperature must be positive.")
        if B_GPa <= 0:
            raise ValueError("Bulk modulus B must be positive.")
        if M <= 0 or rho <= 0:
            raise ValueError("Molar mass M and density rho must be positive.")

        B_pa = B_GPa * 1e9
        # Molar volume: M [g/mol] / rho [g/cm^3] = cm^3/mol -> convert to m^3/mol
        V_molar = (M / rho) * 1e-6

        T_array = np.linspace(1, 1000, 500)
        Cv_array = _debye_Cv(T_array, Theta_D)
        alpha_array = gamma * Cv_array / (3 * B_pa * V_molar)

        idx_300 = np.argmin(np.abs(T_array - 300))
        alpha_300 = alpha_array[idx_300]

        res.add_value("Molar volume (V_molar)", V_molar * 1e6, "cm³/mol")
        res.add_value("Grüneisen parameter (γ)", gamma, "")
        res.add_value("α at 300 K", alpha_300, "1/K")
        res.add_value("α at 300 K (×10⁶)", alpha_300 * 1e6, "ppm/K")

        res.add_text("=== Debye-Grüneisen thermal expansion ===")
        res.add_text(f"  α(300 K) ≈ {alpha_300*1e6:.2f} x 10⁻⁶ K⁻¹")
        res.add_text("  This is a simplified, order-of-magnitude estimate: it assumes a")
        res.add_text("  temperature-independent Grüneisen parameter and an isotropic solid.")
        res.add_text("  Always compare against experimental dilatometry data where available.")

        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(T_array, alpha_array * 1e6, "g-", linewidth=2, label="α(T) (Debye-Grüneisen)")
        ax.plot(300, alpha_300 * 1e6, "ko", markersize=6, label="α at 300 K")
        ax.set_xlabel("Temperature (K)", fontsize=12)
        ax.set_ylabel("Thermal expansion α (×10⁻⁶ K⁻¹)", fontsize=12)
        ax.set_title("Volumetric Thermal Expansion vs Temperature", fontsize=14)
        ax.set_xlim(0, 1000)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)
        fig.tight_layout()
        res.figure = fig
        return res
