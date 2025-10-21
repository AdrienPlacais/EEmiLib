# EEmiLib

**EEmiLib** (Electron EMIssion Library) provides several electron emission models and
a simple interface to fit them to experimental data.
It includes both a _graphical user interface_ (GUI) for ease of use and a
**Python API** for advanced users.

The library focuses on electron emission models relevant to multipactor simulations,
_i.e._ for impinging energies ranging from a few eV to several hundred eV.

This project is still under active development.
I maintain it in my free time, but I'll do my best to answer any questions you
may have.

## Features

- Multiple electron emission models
- Graphical interface for quick model fitting
- Python API for scripting and automation

## Installation

1. Clone the repository
   `git clone git@github.com:AdrienPlacais/EEmiLib.git`
2. Install in editable mode with dependencies
   `cd EEmiLib`
   `pip install -e .[test]`
   - Depending on your shell, you may need to use quotes:
     `pip install -e "[.test]"`
3. Run the tests to ensure everything is working:
   `pytest -m "not implementation"`

## Usage

### Graphical User Interface

To start the GUI:
`eemilib-gui`

![GUI screenshot](./docs/manual/images/gui_example.png)

### Python API

```python
import numpy as np
from eemilib.emission_data import DataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import Vaughan
from eemilib.plotter import PandasPlotter
from eemilib import teey_cu


filepath = [teey_cu / "measured_TEEY_Cu_1_eroded.csv"]

# Object holding filepaths
data_matrix = DataMatrix()
# Indicate that this is TEEY file
data_matrix.set_files(
    filepath, population="all", emission_data_type="Emission Yield"
)
data_matrix.load_data(PandasLoader())

# Plot experimental data
plotter = PandasPlotter()
axes = data_matrix.plot(
    plotter, population="all", emission_data_type="Emission Yield"
)

# Select model and fit
model = Vaughan()
model.find_optimal_parameters(data_matrix)

# Plot fitted data
model.plot(
    plotter,
    population="all",
    emission_data_type="Emission Yield",
    energies=np.linspace(0, 1000, 1001),
    angles=np.linspace(0, 60, 4),
    axes=axes,
)
```

![results screenshot](./docs/manual/images/gui_example_results.png)

## Roadmap/To-Do

- [ ] Handle experimental data with error bars
- [ ] Add control over interpolation of loaded experimental data
- [ ] Optional smoothing of measured data
- [ ] Display additional model information:
  - [ ] Quantitative criteria to assess model quality (e.g., Nicolas Fil's criterion)
  - [ ] Derived quantities such as crossover energies, maximum TEEY, etc.
- Models:
  - [ ] Extend Chung–Everhart fitting to multiple data files
  - [ ] Dionne
  - [ ] Dionne 3D
  - [ ] Dekker
  - [ ] Furman and Pivi
- [ ] `PyPI` release.
- [ ] Different line styles/colors for different populations.
- [ ] `Export` buttons
  - [ ] Tabulated model data.
  - [ ] Model parameters value (makes sense along with an `Import` button).
