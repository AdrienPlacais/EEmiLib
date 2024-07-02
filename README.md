Electron emission fitter
========================
This library offers a way to fit several electron emission models on electron emission data.
Two types of outputs can be generated:
- Text files holding the different emission yields at different impact angles/impact energies.
- Electron emission models parameters.

Scope
=====
Low-energies (multipactor)
Discrimination of secondary, backscattered

Requirements note
=================
### Configuration/inputs
Input via a GUI.
Internally, the configuration will be stored as a dict and saved as a `.toml`.
The configuration file should allow reproducing results.
A `Import` button should allow reusing a previous configuration.

#### Plotter
A scroll-down menu allows setting the `Plotter`.
At first, only `matplotlib.pyplot` will be implemented, but `plotly` or others could be added later.

#### Output folder
Where configuration file, output files, as well as a copy of input files will be saved.

#### Path(s) to TEEY file(s)
| Incident energy (eV) | TEEY @ 0 deg | TEEY @ 20 deg |
| -------------------- | ------------ | ------------- |
| ...                  | ...          | ...           |

- TEEY measurements at various incidence angles are not mandatory.
- Header shall describe measurement process, etc.
- It should be possible to give several files, each corresponding to an incidence angle.
 - Energy points can be different from one file to another.
 - The value of the incidence angle should be the name of the column.
- There is a `Plot` button to show the data understood by the code.

#### Paths to emission energy distribution
| Emission energy (eV) | dE/dW        |               |
| -------------------- | ------------ | ------------- |
| ...                  | ...          | ...           |

- Several columns:
 - For several impact energies?
 - Or for several impact angles?
- There is a `Plot` button to show the data understood by the code.

#### Paths to emission angle distribution
| Emission angle (deg) | dE/dtheta    |               |
| -------------------- | ------------ | ------------- |
| ...                  | ...          | ...           |

- Several columns:
 - For several impact energies?
 - Or for several impact angles?
- There is a `Plot` button to show the data understood by the code.

#### Fitting ranges
Ranges of PE angle and energy on which the fit will be made.
Defined by lower and upper values.

#### Export range
Ranges of PE angle and energy on which the data will be exported.
Defined by lower and upper values as well as number of points.
**Does not concern every output.**
**Will be in an `output` section.**

#### Model
Several tabs allowing to select the model to fit.
Selecting a tab will gray out unused inputs, *e.g.* selecting `Vaughan` will gray out the energy distribution file selector.

#### To do
[ ] Format of input text files? Look at `.hdf5`? Or try to accept `.csv`, `.xlsx`, `.odt`, `.txt`...? Look at my ONERA files.



Roadmap
=======

`v0.1.0`
--------
Roadmap is finished.
It defines, for each version, the functionalities to implement as well as expected behaviors.

`v0.2.0`
--------
The GUI is created, with a placeholder for every input/output.

`v0.2.1`
--------
Plot buttons have a dummy behavior.

`v0.2.2`
--------
Tooltip for every input/output.

**At this stage: send project + roadmap + requirements note to peers.**
**Gather list of testers, list of collaborators.**
**Gather needs of users, update GUI + requirements note.**

`v0.2.3`
--------
GUI and requirements note updated with inputs from peers/users.

`v0.3.0`
--------
GUI produces a dictionary, automatically saved as `.toml` file in `Output folder`.

to put in a version
-------------------
- `Plotter` (`matplotlib` at first, but could also be `plotly`)
- `Reader`
- `Writter` or `Exporter`
- `EEModel`
 - `Vaughan (historical)`
 - `Vaughan (CST)`
 - `Vaughan (SPARK3D)`
 - `Dionne`
 - `Dionne 3D`
- `Import` button

