"""Birch-Murnaghan Equation of State (E-V curve)."""
from typing import Dict
import numpy as np
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure

@register
class BirchMurnaghanEOS(BaseCalculator):
    name = "Equation of State (Birch-Murnaghan)"
    description = (
        "Generates the Energy vs. Volume (E-V) curve using the 3rd-order "
        "Birch-Murnaghan equation. Used to find equilibrium volume and bulk modulus from DFT data."
    )
    required_inputs = ["E0", "V0", "B0", "B0_prime"]
    # Example for Silicon
    example_inputs = {"E0": -215.5, "V0": 40.0, "B0": 99.0, "B0_prime": 4.0}
    expected_summary = "Minimum energy at V0 = 40.0 Å³. E-V curve generated."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        E0, V0 = p["E0"], p["V0"]
        B0_GPa, B0_prime = p["B0"], p["B0_prime"]

        if V0 <= 0:
            raise ValueError("V0 must be positive.")
        if B0_GPa <= 0:
            raise ValueError("B0 must be positive.")

        # Convert B0 from GPa to eV/Å³ (1 eV/Å³ = 160.21766 GPa)
        B0_eV = B0_GPa / 160.21766

        # Generate Volume array (± 10% around V0)
        V_array = np.linspace(0.9 * V0, 1.1 * V0, 200)
        E_array = np.zeros_like(V_array)

        for i, V in enumerate(V_array):
            eta = (V0 / V)**(2/3)
            E_array[i] = E0 + (9 * V0 * B0_eV / 16) * (
                (eta - 1)**3 * B0_prime + (eta - 1)**2 * (6 - 4*eta)
            )

        res.add_value("Equilibrium Volume (V0)", V0, "Å³")
        res.add_value("Equilibrium Energy (E0)", E0, "eV")
        res.add_value("Bulk Modulus (B0)", B0_GPa, "GPa")
        res.add_value("Pressure Derivative (B0')", B0_prime, "")

        res.add_text("The generated plot shows the Energy-Volume relationship.")
        res.add_text("The minimum of the curve corresponds to the equilibrium state.")

        # --- PLOT ---
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(V_array, E_array, 'b-', linewidth=2, label='Birch-Murnaghan Fit')
        ax.plot(V0, E0, 'ro', markersize=8, label='Equilibrium (E0, V0)')

        ax.set_xlabel("Volume (Å³)", fontsize=12)
        ax.set_ylabel("Energy (eV)", fontsize=12)
        ax.set_title("Equation of State: Energy vs. Volume", fontsize=14)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        fig.tight_layout()
        res.figure = fig
        return res
