"""Elastic constants + Born stability criteria for cubic crystals."""
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure
from typing import Dict

@register
class ElasticCubicCalculator(BaseCalculator):
    name = "Elastic constants (cubic)"
    description = (
        "Input C11, C12, C44 (GPa) for a cubic crystal. "
        "Checks Born mechanical stability criteria."
    )
    required_inputs = ["C11", "C12", "C44"]
    example_inputs = {"C11": 250.301, "C12": 129.751, "C44": 143.238}
    expected_summary = "Material is mechanically STABLE (GaN). C11=250.3, C12=129.7, C44=143.2"

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        C11, C12, C44 = p["C11"], p["C12"], p["C44"]

        res.add_value("C11", C11, "GPa")
        res.add_value("C12", C12, "GPa")
        res.add_value("C44", C44, "GPa")

        # Born stability criteria for cubic crystals
        conditions = [
            ("C11 > 0",              C11 > 0),
            ("C44 > 0",              C44 > 0),
            ("C11 - C12 > 0",        C11 - C12 > 0),
            ("C11 + 2*C12 > 0",      C11 + 2*C12 > 0),
        ]

        res.add_text("=== Born stability criteria (cubic) ===")
        all_ok = True
        for expr, ok in conditions:
            tag = "✓" if ok else "✗"
            res.add_text(f"  {tag}  {expr}")
            if not ok:
                all_ok = False

        if all_ok:
            res.add_text("=> Material is mechanically STABLE.")
        else:
            res.add_text("=> Material is MECHANICALLY UNSTABLE.")

        # Plot: bar chart of the three constants
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        labels = ["C11", "C12", "C44"]
        vals = [C11, C12, C44]
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
        ax.bar(labels, vals, color=colors)
        ax.set_ylabel("Value (GPa)")
        ax.set_title("Elastic constants")
        for i, v in enumerate(vals):
            ax.text(i, v + 2, f"{v:.2f}", ha="center", fontsize=9)
        fig.tight_layout()
        res.figure = fig
        return res
