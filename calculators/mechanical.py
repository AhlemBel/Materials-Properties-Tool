"""Bulk, shear, Young moduli + Poisson ratio from C11, C12, C44 (Voigt–Reuss–Hill)."""
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure
from typing import Dict


@register
class MechanicalFromElastic(BaseCalculator):
    name = "Mechanical moduli (VRH)"
    description = (
        "Derives Bulk (B), Shear (G), Young (E) moduli and Poisson ratio (ν) "
        "from cubic elastic constants using Voigt–Reuss–Hill averages."
    )
    required_inputs = ["C11", "C12", "C44"]
    example_inputs = {"C11": 250.301, "C12": 129.751, "C44": 143.238}
    expected_summary = "B_Hill ≈ 169.9 GPa, G_Hill ≈ 101.2 GPa. B/G = 1.68 (BRITTLE behavior)."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        C11, C12, C44 = p["C11"], p["C12"], p["C44"]

        if C11 - C12 == 0:
            raise ValueError("C11 - C12 cannot be zero (division by zero in S11/S12).")
        if C44 <= 0:
            raise ValueError("C44 must be positive.")

        # Voigt
        B_V = (C11 + 2*C12) / 3
        G_V = (C11 - C12 + 3*C44) / 5
        # Reuss
        B_R = B_V                                   # for cubic, B_V == B_R
        S11 = (C11 + C12) / ((C11 - C12)*(C11 + 2*C12))
        S12 = -C12 / ((C11 - C12)*(C11 + 2*C12))
        S44 = 1 / C44
        # NOTE: the Reuss shear modulus for a cubic crystal is
        #   1/G_R = (4*(S11 - S12) + 3*S44) / 5
        # An earlier version of this file omitted the "-4*S12" term, which
        # overestimated G_R (and therefore G_Hill) for every material with C12 != 0.
        G_R = 5 / (4*(S11 - S12) + 3*S44)
        # Hill
        B = (B_V + B_R) / 2
        G = (G_V + G_R) / 2

        E = 9*B*G / (3*B + G)
        nu = (3*B - 2*G) / (2*(3*B + G))

        res.add_value("B_V (Voigt)",  B_V, "GPa")
        res.add_value("B_R (Reuss)",  B_R, "GPa")
        res.add_value("B (Hill)",     B,   "GPa")
        res.add_value("G_V (Voigt)",  G_V, "GPa")
        res.add_value("G_R (Reuss)",  G_R, "GPa")
        res.add_value("G (Hill)",     G,   "GPa")
        res.add_value("E (Young)",    E,   "GPa")
        res.add_value("ν (Poisson)",  nu,  "")

        res.add_text("=== Ductility check (Pugh's criterion) ===")
        if B / G > 1.75:
            res.add_text(f"  B/G = {B/G:.2f} > 1.75  =>  DUCTILE behavior")
        else:
            res.add_text(f"  B/G = {B/G:.2f} ≤ 1.75  =>  BRITTLE behavior")

        # Plot
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        names = ["B", "G", "E"]
        vals  = [B, G, E]
        ax.bar(names, vals, color=["#4c72b0", "#dd8452", "#55a868"])
        ax.set_ylabel("GPa")
        ax.set_title("Derived mechanical moduli (Hill)")
        for i, v in enumerate(vals):
            ax.text(i, v + 2, f"{v:.1f}", ha="center", fontsize=9)
        fig.tight_layout()
        res.figure = fig
        return res
