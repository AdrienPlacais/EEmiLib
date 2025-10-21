Chung and Everhart
==================

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This is a model for emission energy distribution of SEs :cite:`Chung1974`.
It does not take into account incidence angle of PEs.

Input files
-----------

You must provide an emission energy distribution at normal incidence.
Currently, the fitting on several emission distribution files at different PE energies is not supported.

+-----------------------------+---------------+-----------------------------+---------------------------+
|                             |Emission Yield |Emission energy distribution |Emission angle distribution|
+=============================+===============+=============================+===========================+
| "True" secondaries          | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Elastically backscattered   | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Inelastically backscattered | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Total                       | ❌            | ✅                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+

Definitions
-----------

Emission energy distribution is given by:

.. math::

    f(E_\mathrm{SE}) = \frac{E_\mathrm{SE}}{\left( E_\mathrm{SE} + W_f \right)^4}


:math:`W_f` is the material work function in :unit:`eV`.
In order to set it's maximum to unity, we scale it by :math:`256W_f/27`.

Model parameters
----------------

The parameters list is dynamically created here: :py:mod:`Chung and Everhart API documentation<.chung_and_everhart>`.

To-do list
----------

.. todo::
   - Allow fitting on several distribution files with different PE energy.
   - Set up tests.
