"""Elastic anisotropy indices for cubic crystals (Zener ratio & Universal Anisotropy Index)."""
from typing import Dict
from .base import BaseCalculator, CalculatorResult, register
from matplotlib.figure import Figure


@register
class AnisotropyCalculator(BaseCalculator):
    name = "Elastic Anisotropy (Zener & Universal Index)"
    description = (
        "Quantifies how directionally dependent (anisotropic) a cubic crystal's elastic "
        "response is, using the Zener ratio (A) and the Universal Anisotropy Index (A^U) "
        "of Ranganathan & Ostoja-Starzewski (2008). Reuses the same C11, C12, C44 inputs "
        "as the other cubic-crystal calculators."
    )
    required_inputs = ["C11", "C12", "C44"]
    example_inputs = {"C11": 250.301, "C12": 129.751, "C44": 143.238}
    expected_summary = "Zener A ≈ 2.38 and Universal Index A^U ≈ 0.96 => clearly anisotropic (A=1, A^U=0 would be isotropic)."

    def calculate(self, p: Dict[str, float]) -> CalculatorResult:
        res = CalculatorResult()
        C11, C12, C44 = p["C11"], p["C12"], p["C44"]

        if C11 - C12 == 0:
            raise ValueError("C11 - C12 cannot be zero (division by zero in the Zener ratio).")
        if C44 <= 0:
            raise ValueError("C44 must be positive.")

        # Zener anisotropy ratio: A = 1 for a perfectly isotropic cubic crystal
        A_zener = 2 * C44 / (C11 - C12)

        # Voigt / Reuss bounds, using the same (corrected) VRH relations as the
        # "Mechanical moduli (VRH)" calculator: G_R = 5 / (4*(S11-S12) + 3*S44).
        B_V = (C11 + 2*C12) / 3
        G_V = (C11 - C12 + 3*C44) / 5

        B_R = B_V  # identical to B_V for cubic symmetry
        S11 = (C11 + C12) / ((C11 - C12) * (C11 + 2*C12))
        S12 = -C12 / ((C11 - C12) * (C11 + 2*C12))
        S44 = 1 / C44
        G_R = 5 / (4 * (S11 - S12) + 3 * S44)

        # Universal Anisotropy Index (Ranganathan & Ostoja-Starzewski, PRL 101, 055504, 2008)
        A_U = 5 * (G_V / G_R) + (B_V / B_R) - 6

        res.add_value("Zener ratio (A)", A_zener, "")
        res.add_value("G_Voigt", G_V, "GPa")
        res.add_value("G_Reuss", G_R, "GPa")
        res.add_value("Universal Anisotropy Index (A^U)", A_U, "")

        res.add_text("=== Interpretation ===")
        res.add_text("  A = 1 and A^U = 0 both correspond to a perfectly elastically isotropic crystal.")
        if abs(A_zener - 1) < 0.1:
            res.add_text(f"  Zener ratio A = {A_zener:.3f} is close to 1  =>  nearly isotropic.")
        else:
            res.add_text(f"  Zener ratio A = {A_zener:.3f} deviates noticeably from 1  =>  elastically anisotropic.")
        res.add_text(f"  Universal Anisotropy Index A^U = {A_U:.3f} (0 = isotropic; larger = more anisotropic).")
        res.add_text("  Note: there is no single universally agreed cutoff for 'strongly' anisotropic —")
        res.add_text("  A^U and A are best used to COMPARE materials, not as a pass/fail threshold.")

        # Plot: anisotropy indices vs. the isotropic reference line
        fig = Figure(figsize=(5, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(["A (Zener)", "A^U (Universal)"], [A_zener, A_U], color=["#6a51a3", "#3182bd"])
        ax.axhline(1, color="gray", linestyle="--", linewidth=1, label="A = 1 (isotropic ref.)")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_ylabel("Anisotropy index")
        ax.set_title("Elastic anisotropy indices")
        ax.legend(fontsize=8)
        fig.tight_layout()
        res.figure = fig
        return res
