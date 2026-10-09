"""Streamlit frontend for the Materials Properties Deduction Tool.

This is a THIRD UI on top of the exact same physics engine used by main.py
(Tkinter) and gradio_app.py (Gradio) -- it imports calculators/ unchanged and
adds no physics logic here, per the project's modularity rule.

Why this exists: Hugging Face Spaces changed its policy so that new free
personal accounts can no longer create a plain "CPU Basic" Gradio Space (only
a 2-Space "ZeroGPU" allowance for accounts >=30 days old, or a paid PRO plan).
Streamlit Community Cloud has no such paid gate -- unlimited public apps, free,
just needs a public GitHub repo -- so this file lets you deploy the same tool
there with zero changes to the physics.

Run locally with:
    streamlit run streamlit_deploy/streamlit_app.py
"""
import os
import sys

# Make `from calculators import ...` work when this file is launched directly
# by Streamlit (which does not add the repo root to sys.path on its own).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

# Import all calculators so they self-register (same imports as main.py/gradio_app.py)
from calculators import (  # noqa: F401
    elastic, mechanical, debye, hardness, eos, heat_capacity,
    anisotropy, thermal_expansion,
)
from calculators.base import REGISTRY

st.set_page_config(page_title="Materials Properties Tool", page_icon="🔬", layout="wide")

st.title("🔬 Materials Properties Deduction Tool")
st.caption("Select a property, load an example, and get instant results with plots.")

calc_names = list(REGISTRY.keys())
selected_name = st.selectbox("1. Select Property", calc_names, key="calc_select")
calc = REGISTRY[selected_name]
st.info(calc.description)

st.subheader("2. Input Parameters")


def _key(param: str) -> str:
    """Session-state key, namespaced per calculator so switching calculators
    doesn't leak one calculator's numbers into another's identically-named
    parameter (e.g. both Elastic constants and Mechanical moduli use C11)."""
    return f"{selected_name}__{param}"


col_load, col_clear = st.columns([1, 1])
load_clicked = col_load.button("📥 Load Example", width="stretch")
clear_clicked = col_clear.button("🗑 Clear Inputs", width="stretch")

# Button clicks must update session_state BEFORE the number_input widgets below
# are instantiated in this same script run -- Streamlit re-runs top to bottom
# on every interaction, and a widget's `key` "owns" its value once created.
if load_clicked:
    if calc.example_inputs:
        for param, val in calc.example_inputs.items():
            st.session_state[_key(param)] = float(val)
        st.success(f"Example loaded! Expected: {calc.expected_summary}")
    else:
        st.warning("No example data available for this calculator.")

if clear_clicked:
    for param in calc.required_inputs:
        st.session_state[_key(param)] = 0.0

# Dynamic input grid, same idea as main.py's dynamic Tkinter fields.
params = {}
PARAMS_PER_ROW = 5
required = calc.required_inputs
for row_start in range(0, len(required), PARAMS_PER_ROW):
    row_params = required[row_start:row_start + PARAMS_PER_ROW]
    cols = st.columns(len(row_params))
    for col, param in zip(cols, row_params):
        # Seed a default ONLY if this key has never been set, then let the
        # widget itself own the value via `key=` from here on. Passing both
        # `value=` and a pre-existing `key=` is a Streamlit anti-pattern that
        # raises "created with a default value but also had its value set via
        # the Session State API".
        st.session_state.setdefault(_key(param), 0.0)
        params[param] = col.number_input(param, key=_key(param), format="%.6g")

st.subheader("3. Results")

if st.button("▶ CALCULATE", type="primary"):
    try:
        result = calc.calculate(params)
    except ZeroDivisionError:
        st.error(
            "Division by zero. Check your inputs (e.g. C11 = C12, or a modulus "
            "entered as 0) and try again."
        )
    except Exception as e:
        st.error(f"Calculation error: {e}")
    else:
        left, right = st.columns([1, 1])
        with left:
            st.markdown("**Calculated Values**")
            st.table(
                {
                    "Value": list(result.values.keys()),
                    "Result": [
                        f"{v:.4f}{(' ' + u) if u else ''}"
                        for v, u in result.values.values()
                    ],
                }
            )
            st.markdown("**Conclusions & Analysis**")
            for line in result.text:
                st.text(line)
        with right:
            if result.figure is not None:
                st.pyplot(result.figure, width="stretch")
