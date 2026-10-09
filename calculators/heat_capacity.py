"""Debye Model for Heat Capacity (Cv vs T plot)."""
from typing import Dict
import numpy as np
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure

# numpy 2.0 renamed trapz -> trapezoid (trapz is removed in numpy >= 2.0).
# Keep this working across numpy 1.x and 2.x installs (e.g. Hugging Face Spaces
# may pin a different numpy version than a user's local machine).
_trapz = getattr(np, "trapezoid", None) or np.trapz

@register
class DebyeHeatCapacity(BaseCalculator):
    name = "Heat Capacity (Debye Model)"
    description = (
        "Calculates and plots the Molar Heat Capacity (Cv) vs Temperature (T) "
        "using the Debye model. Requires the Debye temperature (Θ_D)."
    )
    required_inputs = ["Theta_D"]
    # Example for Silicon (Θ_D ≈ 645 K)
    example_inputs = {"Theta_D": 645.0}
    expected_summary = "Cv at 300K ≈ 19.8 J/mol·K (Dulong-Petit limit is ~24.9). Plot generated."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        Theta_D = p["Theta_D"]

        if Theta_D <= 0:
            raise ValueError("Debye temperature must be positive.")

        R = 8.314  # Gas constant (J/mol·K)
        T_array = np.linspace(1, 1000, 500) # 1K to 1000K
        Cv_array = np.zeros_like(T_array)

        with np.errstate(over="ignore"):
            for i, T in enumerate(T_array):
                x_max = Theta_D / T
                # Numerical integration using numpy trapz / trapezoid.
                x = np.linspace(0.001, x_max, 1000)
                # Mathematically identical to x^4*e^x / (e^x-1)^2, but this form
                # (via sinh) stays finite for the large x reached at low T instead
                # of overflowing exp(x) first and dividing inf/inf.
                y = x**4 / (4 * np.sinh(x / 2) ** 2)
                integral = _trapz(y, x)
                Cv_array[i] = 9 * R * (T / Theta_D)**3 * integral

        # Find Cv at 300K (Room temp)
        idx_300 = np.argmin(np.abs(T_array - 300))
        Cv_300 = Cv_array[idx_300]

        res.add_value("Debye Temperature (Θ_D)", Theta_D, "K")
        res.add_value("Cv at 300 K (Room Temp)", Cv_300, "J/(mol·K)")
        res.add_value("Dulong-Petit Limit (3R)", 3*R, "J/(mol·K)")

        res.add_text("=== Thermodynamic Analysis ===")
        if Cv_300 > 0.9 * (3*R):
            res.add_text(f"  Cv at 300K is >90% of the Dulong-Petit limit (3R).")
            res.add_text("  => The material behaves classically at room temperature.")
        else:
            res.add_text(f"  Cv at 300K is significantly below the Dulong-Petit limit.")
            res.add_text("  => Quantum effects are still relevant at room temperature.")

        # --- PLOT ---
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(T_array, Cv_array, 'r-', linewidth=2, label=f'Θ_D = {Theta_D} K')
        ax.axhline(3*R, color='gray', linestyle='--', label='Dulong-Petit Limit (3R)')
        ax.plot(300, Cv_300, 'ko', markersize=6, label='Cv at 300 K')

        ax.set_xlabel("Temperature (K)", fontsize=12)
        ax.set_ylabel("Molar Heat Capacity Cv (J/mol·K)", fontsize=12)
        ax.set_title("Debye Heat Capacity vs Temperature", fontsize=14)
        ax.set_xlim(0, 1000)
        ax.set_ylim(0, 30)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        fig.tight_layout()
        res.figure = fig
        return res
