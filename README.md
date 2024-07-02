Electron emission fitter
========================
This software gathers several electron emission models.
They can be fitted on data files (generally experimental).

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
The name of the version and the commit number should appear in the configuration file.

#### Plotter
A scroll-down menu allows setting the `Plotter`.
At first, only `matplotlib.pyplot` will be implemented, but `plotly` or others could be added later.

#### Output folder
Where configuration file, output files, as well as a copy of input files will be saved.

#### Input files
A 4\*3 matrix:
|                           |Emission Yield |Emission energy distribution |Emission angle distribution|
|---------------------------|---------------|-----------------------------|---------------------------|
|"True" secondaries         |               |                             |                           |
|Elastically backscattered  |               |                             |                           |
|Inelastically backscattered|               |                             |                           |
|Total                      |               |                             |                           |

You have to enter files according to the desired model.
Some examples.

For Vaughan:
|                           |Emission Yield |Emission energy distribution |Emission angle distribution|
|---------------------------|---------------|-----------------------------|---------------------------|
|"True" secondaries         | ❌            |❌                           |❌                         |
|Elastically backscattered  | ❌            |❌                           |❌                         |
|Inelastically backscattered| ❌            |❌                           |❌                         |
|Total                      | ✅            |❌                           |❌                         |

For Dionne 3D:
|                           |Emission Yield |Emission energy distribution |Emission angle distribution|
|---------------------------|---------------|-----------------------------|---------------------------|
|"True" secondaries         | ❌            |❌                           |❌                         |
|Elastically backscattered  | ✅            |❌                           |❌                         |
|Inelastically backscattered| ✅            |❌                           |❌                         |
|Total                      | ✅            |❌                           |❌                         |

For Chung and Everhart:
|                           |Emission Yield |Emission energy distribution |Emission angle distribution|
|---------------------------|---------------|-----------------------------|---------------------------|
|"True" secondaries         | ❌            |✅                           |❌                         |
|Elastically backscattered  | ❌            |❌                           |❌                         |
|Inelastically backscattered| ❌            |❌                           |❌                         |
|Total                      | ❌            |❌                           |❌                         |

Note: the idea of this software is to fit a model on experimental data.
**However**, if you want to plot/tabulate a model when you already know the model parameters:

1. Feed in dummy electron emission files.
2. Enter the desired values for the different parameters with very tight lower/upper boundaries.
3. Click on `Fit!`.
This is not really a fit, but you will plot the model with the desired parameters values.
And you can click `Export tabulated` to save tabulated values.

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

### Model tabs
In every `Model` tab, there is the list of the model parameters.

#### Model parameters
A first box retaining the value is filled in by the `Fit!` button, but user can change it manually.
Two cases define lower/upper values, which can be infinity (to deactivate limit).
Default value comes from associated paper, but can be modified by user.

#### `Fit!`
The `Fit!` button will fit the model parameters on the given data.
It fills in the values of the models parameters.

#### `Plot`
This button plots the data from measurement files, and on top of it the modelled data (dashed).
Vaughan will only plot the TEEY, but Dionne 3D will create TEEY, EBEEY, IBEEY, SEEY on the same plot, and angular distribution, and energy distribution.
If relatable, the figure should hold an angle and/or energy box where we can set what we want to plot.

#### `Export tabulated`
Saves tabulated modelled data in `Output folder`.
Proper format?

#### `Save model parameters`
Saves model parameters in `Output folder`.
Proper format?

#### To do
[ ] Format of input text files? Look at `.hdf5`? Or try to accept `.csv`, `.xlsx`, `.odt`, `.txt`...? Look at my ONERA files.
[ ] Format of output text files?

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

