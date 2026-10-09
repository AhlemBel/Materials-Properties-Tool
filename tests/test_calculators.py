"""Headless regression test for the physics engine (no Tkinter/Gradio needed).

Runs every registered calculator on its own example_inputs, checks that it
doesn't crash and doesn't silently miss an example value, and prints the
results next to each calculator's expected_summary so a human can eyeball
them. Run from anywhere with:

    python tests/test_calculators.py
"""
import os
import sys

# Make `from calculators import ...` work whether this is run from the repo
# root or from inside tests/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")  # no display needed

import warnings

# Import all calculators so they register themselves.
from calculators import elastic, mechanical, debye, hardness, eos, heat_capacity  # noqa: F401
from calculators import anisotropy, thermal_expansion  # noqa: F401
from calculators.base import REGISTRY

failures = []

for name, calc in REGISTRY.items():
    print("=" * 70)
    print(name)
    print(calc.description)
    print("required_inputs:", calc.required_inputs)
    print("example_inputs:", calc.example_inputs)

    missing = [k for k in calc.required_inputs if k not in calc.example_inputs]
    if missing:
        failures.append(f"{name}: missing example_inputs for {missing}")
        print(f"!! MISSING example_inputs for: {missing}")
        continue

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", RuntimeWarning)  # catch overflow/div-by-zero etc.
            result = calc.calculate(dict(calc.example_inputs))
    except Exception as e:
        failures.append(f"{name}: {type(e).__name__}: {e}")
        print(f"!! CALCULATION FAILED: {type(e).__name__}: {e}")
        continue

    for k, (v, u) in result.values.items():
        print(f"  {k:35s} = {v:>14.5f} {u}")
    for line in result.text:
        print("   ", line)
    print("expected_summary:", calc.expected_summary)

    if result.figure is None:
        failures.append(f"{name}: calculate() returned no figure")
        print("!! NO FIGURE produced")

print("=" * 70)
print(f"Total calculators registered: {len(REGISTRY)}")

if failures:
    print("\nFAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)

print("\nAll calculators ran cleanly.")
