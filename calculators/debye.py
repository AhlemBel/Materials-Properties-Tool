"""Debye Temperature from elastic moduli and density."""
from typing import Dict
import math
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure

@register
class DebyeTemperatureCalculator(BaseCalculator):
    name = "Debye Temperature (Semi-empirical)"
    description = (
        "Calculates Debye temperature (Θ_D) from Bulk (B) and Shear (G) moduli, "
        "density (ρ), molar mass M, and n = number of atoms PER FORMULA UNIT "
        "(e.g. n=1 for an element like Si or Fe, n=2 for a binary 1:1 compound "
        "like GaN or NaCl, n=5 for an ABX3 perovskite) — M must be the molar mass "
        "of that same formula unit, NOT the number of atoms in the crystallographic "
        "unit cell. Standard post-processing for DFT phonon calculations."
    )
    required_inputs = ["B", "G", "rho", "M", "n"]
    # Example for Silicon: elemental solid, so n=1 formula unit = 1 atom,
    # and M=28.085 g/mol is the molar mass of that one atom.
    # (A previous version of this example used n=2, which silently double-counted
    # the atom density and overestimated Theta_D by 2**(1/3) ~ 26%.)
    example_inputs = {"B": 99.0, "G": 67.0, "rho": 2.33, "M": 28.085, "n": 1} # Silicon
    expected_summary = "Θ_D ≈ 651 K (Silicon, from these example B/G). Experimental Si is ~645 K."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        B, G = p["B"], p["G"]
        rho, M, n = p["rho"], p["M"], p["n"]

        if B <= 0 or G <= 0:
            raise ValueError("B and G must be positive.")
        if rho <= 0 or M <= 0 or n <= 0:
            raise ValueError("rho, M and n must be positive.")

        # Unit conversions: B, G in GPa -> Pa (*1e9). rho in g/cm3 -> kg/m3 (*1000)
        B_pa = B * 1e9
        G_pa = G * 1e9
        rho_kg = rho * 1000

        # Acoustic velocities (m/s)
        v_l = math.sqrt((B_pa + 4/3 * G_pa) / rho_kg)
        v_t = math.sqrt(G_pa / rho_kg)

        # Mean acoustic velocity
        v_m = (1/3 * (2/v_t**3 + 1/v_l**3))**(-1/3)

        # Constants
        h = 6.62607015e-34  # Planck constant (J s)
        k_B = 1.380649e-23  # Boltzmann constant (J/K)
        N_A = 6.02214076e23 # Avogadro constant (mol^-1)

        # Number density (atoms/m^3). M is in g/mol -> kg/mol is M/1000
        n_0 = (n * N_A * rho_kg) / (M / 1000)

        # Debye Temperature (K)
        theta_D = (h / k_B) * ((3 * n_0) / (4 * math.pi))**(1/3) * v_m

        res.add_value("Longitudinal vel. (v_l)", v_l, "m/s")
        res.add_value("Transverse vel. (v_t)", v_t, "m/s")
        res.add_value("Mean acoustic vel. (v_m)", v_m, "m/s")
        res.add_value("Debye Temperature (Θ_D)", theta_D, "K")

        res.add_text(f"Calculated using standard VRH acoustic velocity model.")

        # Plot
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        labels = ["v_l", "v_t", "v_m"]
        vals = [v_l/1000, v_t/1000, v_m/1000] # convert to km/s for plot
        ax.bar(labels, vals, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
        ax.set_ylabel("Velocity (km/s)")
        ax.set_title("Acoustic Velocities")
        for i, v in enumerate(vals):
            ax.text(i, v + 0.2, f"{v:.2f}", ha="center", fontsize=9)
        fig.tight_layout()
        res.figure = fig
        return res
