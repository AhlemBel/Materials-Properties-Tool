"""Tkinter GUI for the materials-properties app."""
import tkinter as tk
from tkinter import ttk, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import all calculators so they register themselves
from calculators import (  # noqa: F401
    elastic, mechanical, debye, hardness, eos, heat_capacity,
    anisotropy, thermal_expansion,
)
from calculators.base import REGISTRY

# Max number of parameter fields placed on one row before wrapping to the next.
# Keeps the input panel from growing wider than the window as calculators
# with more required_inputs are added.
PARAMS_PER_ROW = 5


class MaterialsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Materials Properties Deduction Tool")
        self.geometry("1800x1000")
        self.minsize(1100, 650)  # keep the app usable on smaller screens
        self._build_ui()
        self._refresh_calc_list()

    def _build_ui(self):
        # --- TOP: Calculator Selection ---
        top_frame = ttk.LabelFrame(self, text="1. Select Property to Deduce")
        top_frame.pack(fill="x", padx=10, pady=8)

        self.calc_var = tk.StringVar()
        self.calc_combo = ttk.Combobox(top_frame, textvariable=self.calc_var,
                                       state="readonly", width=45, font=("Arial", 11))
        self.calc_combo.pack(side="left", padx=10, pady=8)
        self.calc_combo.bind("<<ComboboxSelected>>", self._on_calc_change)

        self.btn_example = ttk.Button(top_frame, text="📥 Load Example", command=self._load_example)
        self.btn_example.pack(side="left", padx=5, pady=8)

        self.btn_clear = ttk.Button(top_frame, text="🗑 Clear Inputs", command=self._clear_inputs)
        self.btn_clear.pack(side="left", padx=5, pady=8)

        # --- Calculator description (helps a non-programmer know what they picked) ---
        self.desc_var = tk.StringVar(value="")
        desc_label = ttk.Label(top_frame, textvariable=self.desc_var, wraplength=700,
                                font=("Arial", 9), foreground="#444444")
        desc_label.pack(side="left", padx=15, pady=8, fill="x", expand=True)

        # --- MIDDLE: Dynamic Inputs ---
        self.input_frame = ttk.LabelFrame(self, text="2. Input Parameters")
        self.input_frame.pack(fill="x", padx=10, pady=8)
        self.param_entries = {}

        # --- ACTION ---
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(action_frame, text="▶ CALCULATE", command=self._run).pack(side="left", padx=10)

        self.status_var = tk.StringVar(value="Ready. Select a property to begin.")
        ttk.Label(action_frame, textvariable=self.status_var, foreground="blue",
                  font=("Arial", 10, "italic")).pack(side="left", padx=10)

        # --- BOTTOM: Output ---
        out = ttk.PanedWindow(self, orient="horizontal")
        out.pack(fill="both", expand=True, padx=10, pady=8)

        txt_frame = ttk.LabelFrame(out, text="3. Results & Analysis")
        self.text_out = scrolledtext.ScrolledText(txt_frame, width=60, height=25, font=("Consolas", 11))
        self.text_out.pack(fill="both", expand=True)
        out.add(txt_frame, weight=1)

        plot_frame = ttk.LabelFrame(out, text="4. Visualization (Plots)")
        self.plot_frame = plot_frame
        out.add(plot_frame, weight=2) # Give plot more weight

    def _refresh_calc_list(self):
        names = list(REGISTRY.keys())
        self.calc_combo["values"] = names
        if names:
            self.calc_combo.current(0)
            self._on_calc_change()

    def _on_calc_change(self, event=None):
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        self.param_entries.clear()

        calc_name = self.calc_var.get()
        if not calc_name: return
        calc = REGISTRY[calc_name]

        for i, param in enumerate(calc.required_inputs):
            row, col = divmod(i, PARAMS_PER_ROW)
            ttk.Label(self.input_frame, text=f"{param}:", font=("Arial", 10, "bold")).grid(
                row=row, column=2*col, padx=(15, 5), pady=10, sticky="e")
            entry = ttk.Entry(self.input_frame, width=12, font=("Arial", 11))
            entry.grid(row=row, column=2*col+1, padx=(0, 15), pady=10)
            self.param_entries[param] = entry

        self.desc_var.set(calc.description)
        self.status_var.set(f"Selected: {calc.name}")

    def _load_example(self):
        calc_name = self.calc_var.get()
        if not calc_name: return
        calc = REGISTRY[calc_name]

        if not calc.example_inputs:
            self.status_var.set("No example data available for this calculator.")
            return

        for param, val in calc.example_inputs.items():
            if param in self.param_entries:
                self.param_entries[param].delete(0, tk.END)
                self.param_entries[param].insert(0, str(val))

        # --- NO POPUP, JUST UPDATE STATUS ---
        self.status_var.set(f"Example loaded! Expected: {calc.expected_summary}")

    def _clear_inputs(self):
        for entry in self.param_entries.values():
            entry.delete(0, tk.END)
        self.status_var.set("Inputs cleared.")

    def _collect_params(self):
        params = {}
        missing = []
        invalid = []
        for name, entry in self.param_entries.items():
            v = entry.get().strip()
            if not v:
                missing.append(name)
                continue
            try:
                params[name] = float(v)
            except ValueError:
                invalid.append((name, v))

        if missing or invalid:
            msgs = []
            if missing:
                msgs.append(f"Missing value(s) for: {', '.join(missing)}")
            if invalid:
                bad = ", ".join(f"{n}='{v}'" for n, v in invalid)
                msgs.append(f"Invalid number(s): {bad}")
            raise ValueError(" | ".join(msgs))
        return params

    def _run(self):
        self.text_out.delete("1.0", "end")
        for w in self.plot_frame.winfo_children():
            w.destroy()

        try:
            params = self._collect_params()
        except ValueError as e:
            self.status_var.set(f"Input error: {e}")
            self.text_out.insert("end", f"INPUT ERROR: {e}\n")
            return

        calc_name = self.calc_var.get()
        calc = REGISTRY[calc_name]

        self.text_out.insert("end", f"{'='*20} {calc.name} {'='*20}\n")
        self.text_out.insert("end", f"{calc.description}\n\n")

        try:
            result = calc.calculate(params)
        except ZeroDivisionError:
            self.status_var.set("Calculation failed: division by zero.")
            self.text_out.insert(
                "end",
                "ERROR: Division by zero. Check your inputs (e.g. C11 = C12, or a "
                "modulus entered as 0) and try again.\n",
            )
            return
        except Exception as e:
            self.status_var.set("Calculation failed.")
            self.text_out.insert("end", f"ERROR: {str(e)}\n")
            return

        self.text_out.insert("end", "--- Calculated Values ---\n")
        for name, (val, unit) in result.values.items():
            u = f" {unit}" if unit else ""
            self.text_out.insert("end", f"  {name:<25} = {val:>12.4f}{u}\n")
        self.text_out.insert("end", "\n--- Conclusions & Analysis ---\n")

        for line in result.text:
            self.text_out.insert("end", line + "\n")

        if result.figure is not None:
            canvas = FigureCanvasTkAgg(result.figure, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        self.status_var.set("Calculation successful! Plot generated.")

if __name__ == "__main__":
    app = MaterialsApp()
    app.mainloop()
