"""Headless Streamlit AppTest harness: drives streamlit_deploy/streamlit_app.py
for every calculator (select it, click Load Example, click Calculate) and
checks for uncaught exceptions or st.error() calls. Does not start a browser
or server.

Run from anywhere with:
    python tests/test_streamlit_app.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

import matplotlib
matplotlib.use("Agg")

from streamlit.testing.v1 import AppTest
from calculators import (  # noqa: F401
    elastic, mechanical, debye, hardness, eos, heat_capacity,
    anisotropy, thermal_expansion,
)
from calculators.base import REGISTRY

APP_PATH = os.path.join(REPO_ROOT, "streamlit_deploy", "streamlit_app.py")

failures = []

for name in REGISTRY:
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    if at.exception:
        failures.append(f"{name}: initial run exception: {at.exception}")
        continue

    at.selectbox(key="calc_select").select(name).run()
    if at.exception:
        failures.append(f"{name}: exception after selecting calculator: {at.exception}")
        continue

    # First button in page order is "Load Example"
    at.button[0].click().run()
    if at.exception:
        failures.append(f"{name}: exception after Load Example: {at.exception}")
        continue

    # The "CALCULATE" button is the last button on the page
    at.button[-1].click().run()
    if at.exception:
        failures.append(f"{name}: exception after CALCULATE: {at.exception}")
        continue

    if at.error:
        failures.append(f"{name}: st.error() shown: {[e.value for e in at.error]}")
        continue

    print(f"[ok] {name}")

if failures:
    print("\nFAILURES:")
    for f in failures:
        print(" -", f)
    sys.exit(1)

print(f"\nAll {len(REGISTRY)} calculators work end-to-end through the Streamlit app.")
