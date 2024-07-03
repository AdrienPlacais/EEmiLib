Input files
"""""""""""
A 4\*3 matrix:

+-----------------------------+---------------+-----------------------------+---------------------------+
|                             |Emission Yield |Emission energy distribution |Emission angle distribution|
+=============================+===============+=============================+===========================+
| "True" secondaries          |               | 📁 ``/path/to/file``        |                           |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Elastically backscattered   |               |                             |                           |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Inelastically backscattered |               |                             |                           |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Total                       |               |                             |                           |
+-----------------------------+---------------+-----------------------------+---------------------------+

The different models will need different files (see examples in :ref:`models-link`).
You click on the 📁 to open the File Explorer, but you can also manually type the path.
The magic keyword `%dummy` is allowed.


.. note::

   the idea of this software is to fit a model on experimental data.
   **However**, if you want to plot/tabulate a model when you already know the model parameters:

   #. Feed in dummy electron emission files.
   #. Enter the desired values for the different parameters with very tight lower/upper boundaries.
   #. Click on `Fit!`.

   This is not really a fit, but you will plot the model with the desired parameters values.
   And you can click `Export tabulated` to save tabulated values.

Path(s) to TEEY file(s)
"""""""""""""""""""""""

+----------------------+--------------+---------------+
| Incident energy (eV) | TEEY @ 0 deg | TEEY @ 20 deg |
+======================+==============+===============+
| ...                  | ...          | ...           |
+----------------------+--------------+---------------+

- TEEY measurements at various incidence angles are not mandatory.
- Header shall describe measurement process, etc.
- It should be possible to give several files, each corresponding to an incidence angle.
  - Energy points can be different from one file to another.
  - The value of the incidence angle should be the name of the column.
- There is a `Plot` button to show the data understood by the code.

Paths to emission energy distribution
"""""""""""""""""""""""""""""""""""""

+----------------------+--------------+---------------+
| Emission energy (eV) | dE/dW        |               |
+======================+==============+===============+
| ...                  | ...          | ...           |
+----------------------+--------------+---------------+

- Several columns:
  - For several impact energies?
  - Or for several impact angles?
- There is a `Plot` button to show the data understood by the code.

Paths to emission angle distribution
""""""""""""""""""""""""""""""""""""

+----------------------+--------------+---------------+
| Emission angle (deg) | dE/dtheta    |               |
+======================+==============+===============+
| ...                  | ...          | ...           |
+----------------------+--------------+---------------+

- Several columns:
  - For several impact energies?
  - Or for several impact angles?
- There is a `Plot` button to show the data understood by the code.

