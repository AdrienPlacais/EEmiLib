Interface
*********

.. toctree::
   :maxdepth: 4
   :hidden:

Configuration
"""""""""""""
Internally, the configuration will be stored as a dict and saved to a `.toml`.
The configuration file should allow reproducing results.
An `Import` button should allow reusing a previous configuration.
The name of the version and the commit number should appear in the configuration file.

Plotter
"""""""
A scroll-down menu allows setting the `Plotter`.
At first, only `matplotlib.pyplot` will be implemented, but `plotly` or others could be added later.

Output folder
"""""""""""""
Where configuration file, output files, as well as a copy of input files will be saved.

.. include:: /manual/requirements_note/files.rst

Fitting ranges
""""""""""""""
Ranges of PE angle and energy on which the fit will be made.
Defined by lower and upper values.

Export range
""""""""""""
Ranges of PE angle and energy on which the data will be exported.
Defined by lower and upper values as well as number of points.
**Does not concern every output.**
**Will be in an `output` section.**

Model
"""""
Several tabs allowing to select the model to fit.
Selecting a tab will gray out unused inputs, *e.g.* selecting `Vaughan` will gray out the energy distribution file selector.

Model tabs
^^^^^^^^^^
In every `Model` tab, there is the list of the model parameters.

.. include:: /manual/requirements_note/model_parameters.rst

To do
"""""
* [ ] Format of input text files? Look at `.hdf5`? Or try to accept `.csv`, `.xlsx`, `.odt`, `.txt`...? Look at my ONERA files.
* [ ] Format of output text files?

