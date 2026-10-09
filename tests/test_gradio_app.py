"""End-to-end smoke test for the Gradio web app: builds the Blocks graph and
drives calculate_property()/load_example() for every registered calculator,
the same way a click in the browser would. Does NOT start a web server.

Run from anywhere with:
    python tests/test_gradio_app.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")

from gradio_app import calculate_property, load_example, all_params, update_visibility
from calculators.base import REGISTRY

failures = []

for name in REGISTRY:
    calc = REGISTRY[name]
    example_values = load_example(name)

    text, fig = calculate_property(name, *example_values)
    if text.startswith("❌"):
        failures.append(f"{name}: calculate_property returned an error: {text}")
    if fig is None:
        failures.append(f"{name}: calculate_property returned no figure")

    visibility = update_visibility(name)
    visible_params = {p for p, u in zip(all_params, visibility) if u["visible"]}
    if visible_params != set(calc.required_inputs):
        failures.append(
            f"{name}: visible inputs {visible_params} != required_inputs "
            f"{set(calc.required_inputs)} (did you forget to update all_params?)"
        )

    print(f"[ok] {name}")

if failures:
    print("\nFAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)

print(f"\nAll {len(REGISTRY)} calculators work end-to-end through the Gradio app.")
