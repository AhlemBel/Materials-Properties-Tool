"""Vickers Hardness from Bulk and Shear moduli (Chen's model)."""
from typing import Dict
import math
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure

@register
class HardnessCalculator(BaseCalculator):
    name = "Vickers Hardness (Chen's Model)"
    description = (
        "Estimates Vickers hardness (H_V) from Bulk (B) and Shear (G) moduli "
        "using Chen et al.'s empirical model (2011). Standard DFT post-processing."
    )
    required_inputs = ["B", "G"]
    example_inputs = {"B": 443.0, "G": 535.0} # Diamond
    expected_summary = "H_V ≈ 96.3 GPa (Diamond). Experimental is ~90-100 GPa."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        B, G = p["B"], p["G"]

        if B <= 0 or G <= 0:
            raise ValueError("B and G must be positive.")

        k = G / B
        # Chen's formula: H_V = 2(k^2 * G)^0.585 - 3
        H_V = 2 * ( (k**2 * G)**0.585 ) - 3

        res.add_value("Pugh's ratio (k = G/B)", k, "")
        res.add_value("Vickers Hardness (H_V)", H_V, "GPa")

        res.add_text("=== Hardness Classification ===")
        if H_V > 40:
            res.add_text(f"  H_V = {H_V:.2f} GPa > 40  =>  SUPERHARD material")
        elif H_V > 20:
            res.add_text(f"  H_V = {H_V:.2f} GPa > 20  =>  HARD material")
        else:
            res.add_text(f"  H_V = {H_V:.2f} GPa ≤ 20  =>  SOFT material")

        # Plot
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(["H_V"], [H_V], color="#d62728")
        ax.set_ylabel("Hardness (GPa)")
        ax.set_title("Vickers Hardness")
        ax.axhline(40, color='gray', linestyle='--', label='Superhard threshold (40 GPa)')
        ax.text(0, H_V + 2, f"{H_V:.1f} GPa", ha="center", fontsize=10, fontweight="bold")
        ax.legend()
        fig.tight_layout()
        res.figure = fig
        return res
