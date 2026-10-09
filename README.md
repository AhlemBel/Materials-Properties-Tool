---
title: Materials Properties Deduction Tool
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "6.30.0"
app_file: gradio_app.py
pinned: false
license: mit
---

# 🔬 Materials Properties Deduction Tool

A modular Python app for deducing solid-state physics and materials-science properties
(elastic, mechanical, thermodynamic) from DFT or experimental inputs, checking stability
criteria, and generating publication-ready plots — usable by non-programmers via a
Tkinter desktop UI, a Gradio web UI, or a Streamlit web UI (three frontends, one shared
physics engine — see "Deploying for free", below, for why there are two web options).

## What it can calculate

| Calculator | Inputs | What it gives you |
|---|---|---|
| Elastic constants (cubic) | C11, C12, C44 | Born mechanical-stability check |
| Mechanical moduli (VRH) | C11, C12, C44 | Bulk/Shear/Young moduli, Poisson ratio, Pugh ductility |
| Elastic Anisotropy (Zener & Universal Index) | C11, C12, C44 | Zener ratio A, Universal Anisotropy Index A^U |
| Debye Temperature (Semi-empirical) | B, G, ρ, M, n | Acoustic velocities, Θ_D |
| Heat Capacity (Debye Model) | Θ_D | Cv(T) curve, Dulong–Petit comparison |
| Thermal Expansion Coefficient (Debye-Grüneisen) | Θ_D, B, M, ρ, γ | α(T) curve (order-of-magnitude estimate) |
| Vickers Hardness (Chen's Model) | B, G | H_V and hardness classification |
| Equation of State (Birch-Murnaghan) | E0, V0, B0, B0' | E–V curve, equilibrium volume |

Every calculator ships with a "Load Example" button (realistic numbers, mostly for
cubic GaN / Silicon / Diamond) so you can sanity-check the tool before trusting it
with your own data.

## Architecture

- **Backend**: pure Python, `numpy`, `matplotlib` (`matplotlib.figure.Figure`, not
  `pyplot`, so the same figure object works in both Tkinter and Gradio).
- **Registry pattern**: every calculator lives in its own file in `calculators/`,
  inherits `BaseCalculator`, and self-registers with the `@register` decorator into
  `calculators.base.REGISTRY`. Both UIs just iterate over `REGISTRY` — adding a new
  calculator file is enough to make it appear in both UIs' dropdowns.
- **Frontend 1 (local)**: `main.py`, Tkinter. Builds input fields dynamically from
  each calculator's `required_inputs`, so it needs **no changes** when a new
  calculator is added (as long as it's imported once, to self-register).
- **Frontend 2 (web, Hugging Face Spaces)**: `gradio_app.py`, Gradio Blocks. One
  `gr.Number` component exists per *unique parameter name* across all calculators
  (`all_params`); the dropdown's `.change()` callback shows/hides the ones the
  selected calculator needs.
- **Frontend 3 (web, Streamlit Community Cloud)**: `streamlit_deploy/streamlit_app.py`.
  Builds its input widgets dynamically from `required_inputs`, the same way
  `main.py` does — no `all_params`-style master list needed. Exists because of the
  Hugging Face pricing change described below; it imports `calculators/` unchanged.

## Running locally

```bash
pip install -r requirements.txt

# Desktop (Tkinter) version:
python main.py

# Web (Gradio) version:
python gradio_app.py

# Web (Streamlit) version (needs streamlit_deploy/requirements.txt instead):
pip install -r streamlit_deploy/requirements.txt
streamlit run streamlit_deploy/streamlit_app.py
```

## Tests

Headless regression tests (no display needed) that exercise every calculator's
physics and both web UIs' wiring:

```bash
python tests/test_calculators.py   # runs calculate() with example_inputs for every calculator
python tests/test_gradio_app.py    # drives the Gradio callbacks end-to-end, no browser needed
python tests/test_streamlit_app.py # drives the Streamlit app end-to-end (needs `streamlit` installed)
```

Run these after adding or editing a calculator, and before redeploying.

## Deploying for free

**Important, current as of October 2026:** Hugging Face changed its policy so that
a brand-new **free** personal account can no longer create a plain "CPU Basic"
**Gradio** (or Docker) Space — Gradio/Docker Spaces now require either a **PRO**
subscription, or fall back to a free but capped **ZeroGPU** allowance (max 2
Spaces, and only for accounts that are email-verified and **more than 30 days
old**). Static Spaces (no Python backend) are still free for everyone, but that's
not useful for this app. Source:
[Spaces overview](https://huggingface.co/docs/hub/en/spaces-overview) and
[Spaces ZeroGPU docs](https://huggingface.co/docs/hub/spaces-zerogpu).

That's why this project ships **two** web frontends:

| | Gradio (`gradio_app.py`) on HF Spaces | Streamlit (`streamlit_deploy/`) on Streamlit Community Cloud |
|---|---|---|
| Cost | Free only if your account is PRO, or is >30 days old + email-verified (then capped at 2 Spaces, on ZeroGPU hardware) | **Free, unlimited public apps, no account-age gate** |
| Setup | Pick "Gradio" SDK, select ZeroGPU hardware | Connect a GitHub repo, pick the script path |
| Resource limits | Shared ZeroGPU host (plenty for this CPU-only app) | ~1 GB RAM, sleeps after 12h idle |

If you already qualify for HF's free ZeroGPU allowance (or have PRO), either option
works equally well — this app never requests a GPU, so ZeroGPU hardware runs it
exactly like plain CPU hardware would. **If you're on a brand-new free HF account,
use the Streamlit path below instead** — it has no such restriction.

### Option 1 — Streamlit Community Cloud (recommended: genuinely free, no account-age gate)

1. Put this whole `Materials/` project in a **public** GitHub repository (Streamlit
   Community Cloud deploys from GitHub; private repos need a paid add-on).
2. Create a free account at [share.streamlit.io](https://share.streamlit.io) by
   signing in with GitHub.
3. Click **New app**, choose your repo and branch, and set:
   - **Main file path**: `streamlit_deploy/streamlit_app.py`
   - (Streamlit automatically uses `streamlit_deploy/requirements.txt` because it
     sits next to the main file — you don't need to move anything.)
4. Click **Deploy**. Your app is live at `https://<something>.streamlit.app` in
   about a minute.
5. Any push to that branch redeploys automatically.

### Option 2 — Hugging Face Spaces (free only if ZeroGPU-eligible, or with PRO)

1. Create a free account at [huggingface.co](https://huggingface.co) and verify your email.
   (If it's brand new, you'll need to wait >30 days for the free ZeroGPU allowance,
   or use Option 1 in the meantime.)
2. Click your profile icon → **New Space**.
3. Fill in:
   - **Space name**: anything, e.g. `materials-properties-tool`.
   - **License**: your choice (e.g. MIT).
   - **Select the Space SDK**: **Gradio**.
   - **Space hardware**: pick **ZeroGPU** if that's the free option offered to
     you (it will run this CPU-only app just fine); otherwise **CPU Basic** if
     your account still offers it.
   - Visibility: Public or Private, your choice.
4. Click **Create Space**. You'll land on an empty repo with a "Files" tab.
5. Go to **Files → Add file → Upload files**, and upload, from this project's
   `Materials/` folder (**not** `streamlit_deploy/` — that's for Option 1 only):
   - `gradio_app.py`
   - `requirements.txt`
   - `README.md` (it will ask to replace the auto-generated one — confirm; this
     file's YAML header at the top is what tells the Space which app file to run)
   - the whole `calculators/` folder (drag the folder in; if your browser's
     uploader doesn't accept folders, upload each `calculators/*.py` file one at a
     time and type `calculators/elastic.py` etc. as the destination path — HF
     creates the subfolder automatically)
6. Wait ~1–2 minutes for the "Building" status to turn into "Running". Your app is
   now live at `https://huggingface.co/spaces/<your-username>/<space-name>`.

Prefer git over browser upload for either repeated updates:

```bash
# Hugging Face (pick one SDK/hardware per the note above)
pip install -U "huggingface_hub[cli]"
huggingface-cli login
huggingface-cli repo create materials-properties-tool --type space --space_sdk gradio
git clone https://huggingface.co/spaces/<your-username>/materials-properties-tool
cp -r Materials/* materials-properties-tool/        # repo root, not a "Materials" subfolder
cd materials-properties-tool && git add . && git commit -m "Deploy" && git push
```

```bash
# Streamlit Community Cloud just needs your existing GitHub repo pushed; no extra CLI.
git add . && git commit -m "Add Streamlit frontend" && git push
```

### After deploying

- Both platforms' free tiers sleep after a period of inactivity and wake back up
  automatically on the next visit (a short cold-start delay) — this is normal.
- If you change a `requirements.txt` or add a calculator, just push again (or
  re-upload the changed file on HF); the app rebuilds on its own.
- Keep the pinned versions in sync with what this project was tested against:
  **gradio 6.30.0** (`requirements.txt` / this README's `sdk_version`) and
  **streamlit 1.65.0** (`streamlit_deploy/requirements.txt`).
- Hugging Face's free-tier policy is the kind of thing that changes again without
  much notice — if Option 2 above looks out of date, Option 1 (Streamlit) has no
  comparable restriction as of this writing and needs no HF account at all.

## Adding a new calculator (registry pattern)

1. Create `calculators/your_property.py`:
   ```python
   from .base import BaseCalculator, CalculatorResult, register
   from matplotlib.figure import Figure

   @register
   class YourPropertyCalculator(BaseCalculator):
       name = "Your Property Name"
       description = "One or two sentences a non-programmer can understand."
       required_inputs = ["SomeParam"]        # must match example_inputs keys
       example_inputs = {"SomeParam": 1.23}   # realistic, checkable numbers
       expected_summary = "What a correct run should show, for self-checking."

       def calculate(self, p):
           res = CalculatorResult()
           # ... physics here; wrap risky math (sqrt, division) so it raises a
           # clear ValueError instead of crashing the UI ...
           res.add_value("Result name", value, "unit")
           res.add_text("A conclusion sentence.")
           fig = Figure(figsize=(5, 3.5), dpi=100)   # Figure, not pyplot
           ax = fig.add_subplot(111)
           # ... ax.plot/ax.bar with labeled axes, title, grid ...
           res.figure = fig
           return res
   ```
2. Import it once so it self-registers:
   - `main.py`: add it to the `from calculators import (...)` line (Tkinter needs
     no other change — its inputs are built dynamically).
   - `streamlit_deploy/streamlit_app.py`: same deal — add it to its
     `from calculators import (...)` line and nothing else; its inputs are also
     built dynamically from `required_inputs`.
   - `gradio_app.py`: add the import, and if `required_inputs` introduces a
     parameter name not already in `all_params`, add it there **and** to
     `PARAM_LABELS`. `calculate_property()` builds its parameter dict from
     `all_params` automatically, so that's the only place to touch.
3. Run all three tests — each should report your new calculator as passing:
   ```bash
   python tests/test_calculators.py
   python tests/test_gradio_app.py
   python tests/test_streamlit_app.py
   ```

## Physics notes & formula references

- **VRH averaging (Mechanical moduli / Anisotropy)**: Voigt and Reuss bounds with
  the Hill average; `B_R = B_V` and `1/G_R = (4·(S11−S12) + 3·S44) / 5` for cubic
  symmetry (Hill, 1952).
- **Universal Anisotropy Index A^U** = 5·(G_V/G_R) + (B_V/B_R) − 6
  (Ranganathan & Ostoja-Starzewski, *Phys. Rev. Lett.* **101**, 055504, 2008).
- **Debye temperature from elastic moduli**: standard acoustic-velocity method
  (e.g. Anderson, 1963); Θ_D = (h/k_B)·(3n₀/4π)^(1/3)·v_m, where n₀ is the atomic
  number density. **`n` is the number of atoms per formula unit** (1 for an
  element, 2 for a 1:1 binary compound, etc.) and `M` must be the molar mass of
  that same formula unit — not the count of atoms in the crystallographic unit
  cell (see "Bug fixes" below).
- **Vickers hardness**: Chen, Niu, Li & Li, *Intermetallics* **19**, 1275 (2011),
  H_V = 2·(k²·G)^0.585 − 3, k = G/B.
- **Birch–Murnaghan EOS**: standard 3rd-order form; 1 eV/Å³ = 160.21766 GPa.
- **Debye heat capacity & Debye–Grüneisen thermal expansion**: standard Debye
  integral for Cv(T); α = γ·Cv/(3·B·V_molar). This thermal-expansion estimate
  assumes a temperature-independent Grüneisen parameter and is meant as a rough,
  order-of-magnitude check against experiment, not a precision prediction.

## Bug fixes made during this review

These were found by writing `tests/test_calculators.py` and comparing each
calculator's own output against its own `expected_summary`:

1. **Reuss shear modulus was missing a term.** `mechanical.py` (and the new
   anisotropy calculator, which reuses the same math) computed
   `G_R = 5/(4*S11 + 3*S44)`, omitting `-4*S12`. The correct cubic-symmetry
   formula is `G_R = 5/(4*(S11-S12) + 3*S44)`. This under-counted shear modulus,
   and therefore Young's modulus, Poisson ratio and the B/G ductility ratio, for
   every material with nonzero C12 (i.e. essentially all real materials).
2. **Debye Temperature's `n` parameter was ambiguous and its example was wrong
   for the stated use case.** The docstring called it "atoms per unit cell", but
   the formula needs atoms **per formula unit** (consistent with the molar mass
   `M` you enter). The built-in Silicon example used `n=2` (the diamond-cubic
   unit cell count) together with `M=28.085` (the per-atom molar mass) — an
   inconsistent pairing that overestimated Θ_D by 2^(1/3) ≈ 26%. Fixed the
   docstring and changed the example to `n=1`, consistent with `M` being a
   single Si atom's molar mass.
3. **`numpy.trapz` is removed in NumPy ≥ 2.0** (renamed to `numpy.trapezoid`),
   which this app would hit immediately on a fresh install with a current NumPy.
   `heat_capacity.py` and the new thermal-expansion calculator now use
   `np.trapezoid` with a fallback to `np.trapz` for older NumPy.
4. **Numerical overflow warning** in the Debye heat-capacity integrand at low
   temperature (large `x = Θ_D/T`): `exp(x)` overflows before the division. The
   integrand is now computed as `x⁴ / (4·sinh(x/2)²)`, which is mathematically
   identical but numerically stable (no behavior change, just removes a spurious
   `RuntimeWarning` that would otherwise show up in your deployment logs).
5. A stale/inconsistent `expected_summary` and in-code comment in
   `mechanical.py` were updated to match the corrected numbers.

None of these were "crashes" — the app ran and produced plausible-looking
numbers in all cases, which is exactly why the project's own "Validation
Examples" rule (every calculator must ship a checkable `example_inputs` /
`expected_summary` pair) is worth keeping for every future calculator, too.

## What this tool does *not* do

It does not replace a licensed engineer's or materials scientist's judgment, and
several models here (Chen's hardness model, the Birch-Murnaghan fit, the
Debye-Grüneisen thermal-expansion estimate) are empirical or approximate by
construction — always cross-check against experimental data before using a
result for anything load-bearing (literally or figuratively).
