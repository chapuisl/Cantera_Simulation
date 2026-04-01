# Cantera Combustion Simulation Framework
**Complete User Documentation & Reference Guide**
Version 1.0 — February 2026
Author: Lilian CHAPUIS — IMFT, Toulouse, France

---

## 1. Overview

This framework provides a fully automated, configuration-driven environment for running Cantera-based combustion simulations. It is designed for researchers and engineers who need to study flame dynamics, ignition, species concentrations, and counterflow diffusion flames across a range of operating conditions and chemical kinetics mechanisms.

The framework is structured around a single YAML configuration file (`parameter_coupling.yaml`) that controls every aspect of the simulation: what to compute, under what conditions, with which chemical mechanism, and how to post-process and save the results. No code modification is required between runs.

---

## 2. Architecture — File Structure

| File | Role |
|------|------|
| `parameter_coupling.yaml` | Master configuration file. Defines all simulation parameters, operating conditions, mechanisms, and output settings. |
| `Cantera_proc.py` | Main entry point. Reads the YAML config and orchestrates all simulation runs. |
| `Input_yaml_Reading.py` | Parses and validates the YAML configuration file. Returns a structured dictionary of all parameters. |
| `Available_Kinetic_MECH.py` | Centralized registry mapping short mechanism names to their YAML file paths on disk. |
| `PreProcessing.py` | Prepares gas phase objects and initial conditions before each simulation run. |
| `PostProcessing.py` | Processes raw Cantera output into structured results (flame speed, thickness, emissions, etc.). |
| `Global_plot_figure.py` | Generates summary figures across all conditions and mechanisms. |
| `Verbosity_Level_Plot.py` | Controls live plotting and console output based on the verbosity level. |
| `Graphic_Configuration.py` | Sets global matplotlib style parameters and provides color/line style palettes. |
| `Common_Utils_tools.py` | Utility functions: directory management, file backup, species formatting, input preparation. |

---

## 3. Dependencies & Installation

### 3.1 Required Python Packages

```bash
pip install cantera numpy matplotlib pyyaml colorama
```

| Package | Version | Purpose |
|---------|---------|---------|
| `cantera` | >= 3.0 | Core combustion chemistry and flame solver |
| `numpy` | >= 1.24 | Numerical arrays and linspace generation |
| `matplotlib` | >= 3.7 | Plot generation and post-processing figures |
| `pyyaml` | >= 6.0 | YAML configuration file parsing |
| `colorama` | >= 0.4 | Colored terminal output for verbosity logging |

### 3.2 Kinetic Mechanism Files

All kinetic mechanisms must be available as Cantera-compatible YAML files on your local machine. Their paths are registered in `Available_Kinetic_MECH.py` (see Section 6). The built-in mechanisms (`GRI30`, `h2o2`) ship with Cantera; all custom mechanisms must be downloaded and their paths updated manually.

---

## 4. Quick Start

**Step 1** — Edit `parameter_coupling.yaml` to set your desired simulation types, fuel/oxidizer mixture, operating conditions, mechanisms, and output path.

**Step 2** — Verify that all mechanism paths in `Available_Kinetic_MECH.py` are correct for your machine.

**Step 3** — Launch the main script:

```bash
python Cantera_proc.py
```

The framework reads the YAML file, creates the output directory, runs all enabled simulations across all specified conditions and mechanisms, and saves plots and CSV files to the configured output path.

---

## 5. Configuration File — parameter_coupling.yaml

All simulation behaviour is controlled from this single file.

### 5.1 output — Results Directory

```yaml
output:
  directory: /path/to/results/root
  filename: 100-NH3_00-H2_AIR_Simulation1/
```

`directory` is the root path where all result folders are created. `filename` is the subfolder name for this specific simulation run. The framework creates it automatically and **overwrites it** if it already exists.

---

### 5.2 simulation.type — Enabling/Disabling Simulations

```yaml
simulation:
  type:
    Flame_1D              : true
    Temperature_Adiabatic : true
    Ignition_Delay_time   : true
    Gas_Composition       : true
    Counter_flow          : true
```

| Simulation Type | Description |
|----------------|-------------|
| `Flame_1D` | Freely propagating 1D premixed flame. Computes flame speed, thickness, characteristic time, emissions, and species profiles. |
| `Temperature_Adiabatic` | Equilibrium calculation at constant pressure. Computes adiabatic flame temperature, final density, and enthalpy. |
| `Ignition_Delay_time` | Homogeneous constant-pressure reactor. Computes IDT as a function of temperature, pressure, and equivalence ratio. |
| `Gas_Composition` | Reports species mole fractions in fresh and burnt gas at equilibrium conditions. |
| `Counter_flow` | Counterflow diffusion flame. Computes extinction strain rate and optionally basic diffusion flame profiles. |

---

### 5.3 kinetics — Mechanisms

List the mechanisms to use. Multiple mechanisms can be enabled simultaneously; all results will be computed for each one and overlaid in plots for comparison.

```yaml
kinetics:
  mechanism-1 : ZHU24
  mechanism-2 : STAGNI25
  mechanism-3 : STAGNI20
```

Available mechanism keys (defined in `Available_Kinetic_MECH.py`):

| Key | Description | Species / Reactions |
|-----|-------------|---------------------|
| `GRI30` | Methane/natural gas mechanism (built-in Cantera) | 53 sp. / 325 rxn. |
| `h2o2` | Simplified hydrogen oxidation (built-in Cantera) | 9 sp. / 21 rxn. |
| `SANDIEGO` | San Diego H2 mechanism | 9 sp. / 21 rxn. |
| `STAGNI20` | Stagni 2020 — NH3 pyrolysis and oxidation | 31 sp. / 203 rxn. |
| `STAGNI25` | Stagni 2025 — NH3/H2 pyrolysis and oxidation | 34 sp. / 272 rxn. |
| `ZHU24` | Zhu 2024 — NH3 oxidation + NOx formation | 43 sp. / 312 rxn. |

> ⚠️ To add a new mechanism, register it in `Available_Kinetic_MECH.py` with a short key and its absolute path, then reference the key here.

---

### 5.4 mixture — Fuel and Oxidizer

```yaml
mixture:
  fuel:
    - species  : NH3
      fraction : 1.0
    - species  : H2
      fraction : 0.0
  oxidizer:
    - species  : O2
      fraction : 1.0
    - species  : N2
      fraction : 3.76
```

Fractions do not need to be normalized (Cantera handles normalization internally). Species names must exactly match those defined in the chosen kinetic mechanism.

---

### 5.5 conditions — Operating Conditions

Each simulation type has its own conditions block. Three modes are available for each parameter:

| Mode | YAML syntax | Result |
|------|-------------|--------|
| `single` | `mode: single` / `value: 300` | One value: `[300]` |
| `list` | `mode: list` / `values: [300, 400, 500]` | Explicit list |
| `linspace` | `mode: linspace` / `start: 300` / `end: 1000` / `points: 5` | 5 evenly spaced values |

**Units:** Temperature in K, Pressure in bar, Phi dimensionless, Mass flux in kg/m²/s.

#### Flame_1D / Temperature_Adiabatic / Ignition_Delay_time / Gas_Composition

```yaml
conditions:
  Flame_1D:
    Temperature:
      mode  : list
      values: [300, 500]
    Pressure:
      mode  : list
      values: [1.01325, 2]
    Phi:
      mode  : linspace
      start : 0.8
      end   : 1.5
      points: 25
```

The framework creates a full Cartesian product of Temperature × Pressure × Phi. In the example above: 2 × 2 × 25 = **100 simulation points per mechanism**.

#### Counter_flow

```yaml
conditions:
  Counter_flow:
    Pressure:
      mode  : list
      values: [1.01325, 2]
    Temperature_pairs:
      - [300, 300]       # [T_fuel, T_oxidizer] in K
    Velocity_flux_pairs:
      - [6.0, 3.0]       # [fuel_mass_flux, oxidizer_mass_flux] in kg/m²/s
```

---

### 5.6 outputs — Per-Simulation Output Selection

#### Flame_1D

```yaml
outputs:
  Flame_1D:
    flame_speed    : true    # Laminar burning velocity (m/s)
    flame_thickness: true    # Thermal flame thickness (m)
    flame_time     : true    # Characteristic flame time (s)
    emissions      : true    # NOx and pollutant emissions
    Major_species:
      - 'O2'
      - 'H2O'
      - 'NH3'
    Radicals:
      - 'NO'
      - 'OH'
      - 'NH2'
```

#### Ignition_Delay_time

```yaml
  Ignition_Delay_time:
    IDT_plot          : true    # IDT vs 1000/T Arrhenius plot
    time_evolution    : true    # Species time evolution during ignition
    complementary_plot: true    # Additional diagnostic plots
```

#### Temperature_Adiabatic

```yaml
  Temperature_Adiabatic:
    Final_Temperature: true    # Adiabatic flame temperature vs Phi
    Final_density    : true    # Burnt gas density
    Final_Enthalpy   : true    # Mixture enthalpy
```

#### Gas_Composition

```yaml
  Gas_Composition:
    Fresh_gas: true    # Unburnt mixture composition
    Burn_gas : true    # Equilibrium burnt gas composition
```

#### Counter_flow

```yaml
  Counter_flow:
    Extinction_strain    : true     # Extinction strain rate
    Basic_diffusion_flame: false    # Baseline diffusion flame profile
    Major_species: [...]
    Radicals: [...]
```

> ⚠️ Species names in `Major_species` and `Radicals` must exactly match the mechanism. If a species is absent, a WARNING is printed and it is silently skipped.

---

### 5.7 post_processing

```yaml
post_processing:
  save_plots     : true
  verbosity_level: 3
```

| Level | Output |
|-------|--------|
| `0` | Silent — no console output. |
| `1` | Minimal — simulation milestones only. |
| `2` | Intermediate — species concentrations + basic live monitoring. May slow down computation. |
| `3` | Full debug — all variables, full species tracking, extended thermodynamic and kinetic info. |

---

## 6. Mechanism Registry — Available_Kinetic_MECH.py

This module is the single source of truth for mechanism file paths. To add a new mechanism:

1. Open `Available_Kinetic_MECH.py`.
2. Add a new entry in the `available_mechanisms` dictionary:

```python
def Kinetic_mechanism():
    available_mechanisms = {
        "GRI30"  : "gri30.yaml",
        "MyMech" : "/absolute/path/to/my_mechanism.yaml",
        # ...
    }
    return available_mechanisms
```

3. Reference the new key in `parameter_coupling.yaml` under `kinetics`.

> ⚠️ Always use **absolute paths** for custom mechanisms.

---

## 7. Graphic Configuration — Graphic_Configuration.py

### 7.1 Global Plot Style

```python
from Graphic_Configuration import config_plot
config_plot(style='default', figsize=(12, 8))
```

Sets font sizes (title 40pt, labels 40pt, ticks 36pt), line widths, marker sizes, grid, DPI (500 screen / 300 saved), and background colors globally for all matplotlib figures.

### 7.2 Color Palettes

Each function returns a list of RGB tuples:

| Function | Gradient |
|----------|----------|
| `Black_Gray()` | Black → light gray |
| `Black_Purple()` | Black → gray → violet |
| `Black_Blue()` | Black → gray → blue |
| `Black_Green()` | Black → gray → green |
| `Black_Red()` | Black → gray → red |
| `Black_Orange()` | Black → gray → orange |
| `Blue_Red()` | Blue → red |
| `Ramdom()` | Distinct high-contrast colors |
| `Purple_Black()`, `Blue_Black()`, etc. | Reversed versions of the above |

### 7.3 Line Style Palette

`LineStyles()` returns 9 distinct matplotlib line style definitions, suitable for distinguishing multiple mechanisms or conditions on a single plot.

---

## 8. Utility Module — Common_Utils_tools.py

### 8.1 `backup_file(parameter_coupling, file_name)`

Creates the main results directory. If it already exists, it is **deleted and recreated**. The function:
- Verifies the parameter file exists.
- Creates the main results directory.
- Creates five standardized subdirectories:
  - `01_plot_evolution` — time or phi evolution plots
  - `02_plot_species_evolution` — species concentration plots
  - `03_Other_plot` — miscellaneous figures
  - `04_csv_evolution` — CSV data exports
  - `05_AVBP_Solution` — files formatted for AVBP solver input
- Copies the parameter YAML file into the results directory for traceability.

### 8.2 `create_folder(parent_path, folders)`

Creates a new subdirectory (or nested hierarchy) inside an existing parent directory. Preserves existing directories (no deletion).

### 8.3 `Prepare_simulation_inputs(fuel_list, oxidizer_list, mechanisms_dict)`

Converts parsed fuel/oxidizer lists and mechanism dictionary into formatted data ready for simulation loops and file naming.

```python
fuel_dict, oxidizer_dict, fuel_name_str, oxidizer_name_str, mechanism_names = \
    Prepare_simulation_inputs(fuel_list, oxidizer_list, mechanisms_dict)
```

### 8.4 `list_to_dict(lst)` and `format_dict_components(d)`

`list_to_dict` converts a species list (single or multiple pairs) to a dictionary.
`format_dict_components` formats a composition dictionary into a readable string, e.g. `{'NH3': 1.0, 'H2': 0.0}` → `'1NH3_0H2'`.

---

## 9. YAML Parsing — Input_yaml_Reading.py

`check_file_Parameters_yaml(parameter_coupling)` is the entry point for configuration loading. It:
- Opens and parses the YAML file.
- Validates all required fields (types, allowed values).
- Calls `parse_range()` to convert each condition parameter into a Python list.
- Loads and validates all requested mechanisms against the registry.
- Returns a single structured dictionary used by all downstream modules.

```python
{
  'simulation_type' : dict of bool,
  'path_file'       : {'directory': str, 'filename': str},
  'fuel'            : list of [species, fraction],
  'oxidizer'        : list of [species, fraction],
  'outputs'         : dict of output flags and species lists,
  'conditions'      : dict of parsed condition arrays per simulation type,
  'mechanisms'      : dict mapping mechanism name to file path,
  'save_plot'       : bool,
  'verbosity_level' : int (0–3)
}
```

---

## 10. Typical Workflow

| Step | Action | Module |
|------|--------|--------|
| 1 | Edit `parameter_coupling.yaml` | `parameter_coupling.yaml` |
| 2 | `check_file_Parameters_yaml()` loads and validates all parameters | `Input_yaml_Reading.py` |
| 3 | `backup_file()` creates the output directory tree | `Common_Utils_tools.py` |
| 4 | `Prepare_simulation_inputs()` formats data for loop iteration | `Common_Utils_tools.py` |
| 5 | `PreProcessing` sets up the Cantera gas object per condition | `PreProcessing.py` |
| 6 | Core simulation executed (flame, IDT, adiabatic T, etc.) | `Cantera_proc.py` |
| 7 | `PostProcessing` extracts quantities (flame speed, IDT, emissions...) | `PostProcessing.py` |
| 8 | Figures generated | `Global_plot_figure.py` / `Verbosity_Level_Plot.py` |
| 9 | Results (CSV + PNG) saved under `output/directory/filename/` | `Common_Utils_tools.py` |

---

## 11. Extending the Framework

### Adding a New Simulation Type

1. Add a new key under `simulation.type` in the YAML file.
2. Add a corresponding block under `outputs` and `conditions`.
3. Implement the simulation logic in `Cantera_proc.py`.
4. Add the post-processing logic in `PostProcessing.py`.
5. Add a plotting function in `Global_plot_figure.py` using the palettes from `Graphic_Configuration.py`.

### Adding a New Output Quantity

1. Add a boolean flag under the relevant simulation type in `outputs` in the YAML file.
2. Read the flag in the post-processing module and compute the quantity conditionally.

---

## 12. Known Limitations & Notes

- Mechanism file paths in `Available_Kinetic_MECH.py` are **absolute and machine-specific**. They must be updated when moving the project to a different machine.
- High verbosity levels (2 and 3) significantly slow down computation due to frequent console output and live plotting.
- The output directory is **entirely deleted and recreated** on each run. Back up any results you want to keep before re-running with the same output path.
- Counter-flow simulations are more sensitive to initial conditions than premixed flames. If convergence fails, try adjusting the mass flux pairs.
- Species listed under `Major_species` and `Radicals` that are absent from the chosen mechanism are silently skipped after a WARNING message.

---

## 13. Copyright

© 2026 Lilian CHAPUIS — All Rights Reserved.
IMFT — Institut de Mécanique des Fluides de Toulouse, France.
Unauthorized copying, distribution, modification, or use without prior written permission is strictly prohibited.
This framework is intended solely for use within the associated simulation project developed by the author.

