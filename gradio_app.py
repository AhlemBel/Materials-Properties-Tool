import gradio as gr
from calculators import elastic, mechanical, debye, hardness, eos, heat_capacity
from calculators import anisotropy, thermal_expansion
from calculators.base import REGISTRY

# Define all possible parameters across all calculators.
# IMPORTANT: if you add a new calculator whose required_inputs introduces a
# parameter name that is not already in this list, you must:
#   1. add it to all_params below,
#   2. add a matching gr.Number(...) component in the Blocks layout,
#   3. add it to the `input_map` dict inside calculate_property(),
#   4. add it to the `param_components` list.
all_params = [
    "C11", "C12", "C44", "B", "G", "rho", "M", "n",
    "E0", "V0", "B0", "B0_prime", "Theta_D", "gamma",
]

PARAM_LABELS = {
    "C11": "C11 (GPa)",
    "C12": "C12 (GPa)",
    "C44": "C44 (GPa)",
    "B": "Bulk Modulus B (GPa)",
    "G": "Shear Modulus G (GPa)",
    "rho": "Density ρ (g/cm³)",
    "M": "Molar Mass M (g/mol)",
    "n": "Atoms per formula unit (n)",
    "E0": "E0 (eV)",
    "V0": "V0 (Å³)",
    "B0": "B0 (GPa)",
    "B0_prime": "B0' (Pressure derivative)",
    "Theta_D": "Debye Temp Θ_D (K)",
    "gamma": "Grüneisen parameter (γ)",
}


def update_visibility(calc_name):
    """Dynamically show/hide inputs based on the selected calculator."""
    calc = REGISTRY[calc_name]
    required = calc.required_inputs
    updates = []
    for p in all_params:
        # Show the input if it's required, hide it otherwise
        updates.append(gr.update(visible=(p in required)))
    return updates


def calculate_property(calc_name, *param_values):
    if not calc_name:
        return "Please select a property.", None

    calc = REGISTRY[calc_name]

    # Map the UI inputs (in all_params order) to their parameter names
    input_map = dict(zip(all_params, param_values))

    params = {}
    for req in calc.required_inputs:
        if req in input_map:
            val = input_map[req]
            if val == "" or val is None:
                return f"❌ Missing required input: {req}", None
            try:
                params[req] = float(val)
            except (TypeError, ValueError):
                return f"❌ Invalid number for {req}: '{val}'", None

    try:
        result = calc.calculate(params)
    except ZeroDivisionError:
        return (
            "❌ Division by zero. Check your inputs (e.g. C11 = C12, or a "
            "modulus entered as 0) and try again.",
            None,
        )
    except Exception as e:
        return f"❌ Calculation Error: {str(e)}", None

    # Format text output
    out = f"=== {calc.name} ===\n"
    for name, (val, unit) in result.values.items():
        u = f" {unit}" if unit else ""
        out += f"• {name}: {val:.4f}{u}\n"
    out += "\n--- Analysis & Conclusions ---\n" + "\n".join(result.text)

    return out, result.figure


def load_example(calc_name):
    calc = REGISTRY[calc_name]
    ex = calc.example_inputs
    # Return values in the exact order of all_params
    return [ex.get(p, None) for p in all_params]


# Build the Web UI
with gr.Blocks(title="Materials Properties Tool", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔬 Materials Properties Deduction Tool")
    gr.Markdown("Select a property, load an example, and get instant results with plots.")

    with gr.Row():
        with gr.Column(scale=1):
            calc_dropdown = gr.Dropdown(
                choices=list(REGISTRY.keys()),
                label="1. Select Property",
                value=list(REGISTRY.keys())[0]
            )
            calc_description = gr.Markdown(
                list(REGISTRY.values())[0].description
            )

            gr.Markdown("### 2. Input Parameters")

            # Check which inputs the very first calculator needs to set initial visibility
            first_calc_req = list(REGISTRY.values())[0].required_inputs

            # Create one input component per entry in all_params (they hide/show dynamically)
            param_components = [
                gr.Number(label=PARAM_LABELS[p], visible=(p in first_calc_req))
                for p in all_params
            ]

            with gr.Row():
                load_btn = gr.Button("📥 Load Example", variant="secondary")
                calc_btn = gr.Button("▶ CALCULATE", variant="primary")

        with gr.Column(scale=2):
            text_output = gr.Textbox(label="3. Results & Analysis", lines=15)
            plot_output = gr.Plot(label="4. Visualization")

    # --- EVENT LISTENERS ---

    # 0. Show the selected calculator's description (helps non-programmer users
    #    understand what they're about to compute and what units are expected)
    calc_dropdown.change(
        lambda name: REGISTRY[name].description,
        inputs=[calc_dropdown],
        outputs=[calc_description],
    )

    # 1. When dropdown changes, update the visibility of the inputs
    calc_dropdown.change(
        update_visibility,
        inputs=[calc_dropdown],
        outputs=param_components
    )

    # 2. When Load Example is clicked, fill the inputs
    load_btn.click(
        load_example,
        inputs=[calc_dropdown],
        outputs=param_components
    )

    # 3. When Calculate is clicked, run the physics engine
    calc_btn.click(
        calculate_property,
        inputs=[calc_dropdown] + param_components,
        outputs=[text_output, plot_output]
    )

if __name__ == "__main__":
    # On Hugging Face Spaces, the Space itself serves the public URL, so
    # share=True is neither needed nor recommended there (it's only useful
    # for sharing a temporary 72-hour link from your own machine).
    demo.launch()
