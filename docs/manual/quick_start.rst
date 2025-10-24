.. _quick-start-link:

Quick start
***********

.. toctree::
   :maxdepth: 4
   :hidden:

From the a Python environment with `EEmiLib`, run the `eemilib-gui` command.
The following window should open.

.. image:: ../images/gui_example.png
   :width: 600
   :alt: GUI screen shot
   :align: center

Load experimental data
==========================

1. Select your data :class:`.Loader`.

 - The choice of the loader depends on the format of your data file.
   By default, use :class:`.pandas_loader.PandasLoader`.
   It will work with the example data provided in `cu/` and `ag/`.

2. Select your electron emission :class:`.Model`.

 - Changing the model updates the `Files selection matrix`, according to the experimental files required by the model.
 - Changing the model also updates the list of parameters in `Model configuration`.

3. Select the file(s) to be loaded in the `Files selection matrix`.
4. Load the data by clicking `Load data`.
5. Plot the loaded data to check that it is properly understood by clicking `Plot file`.

Fit the model on the data
=========================

6. Click `Fit!` to fit the model on the data.

 - It should update the values of the model parameters in `Model configuration`.
 - You can manually modify those values.
 - You can `lock` a parameter to a specific value, change the upper and lower bounds, and rerun the `Fit!`.

7. Plot the modelled data with `Plot model`.

.. image:: ../images/gui_example_results.png
   :width: 600
   :alt: Corresponding figure
   :align: center
