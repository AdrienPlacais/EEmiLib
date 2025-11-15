Maxwellian distribution
=======================

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This is a model for emission energy distribution of |SEs|.
It does not take into account incidence angle of |PEs|.

Input files
-----------

You must provide an emission energy distribution at normal incidence.
Currently, the fitting on several emission distribution files at different |PE| energies is not supported.

+-----------------------------+---------------+-----------------------------+---------------------------+
|                             |Emission Yield |Emission energy distribution |Emission angle distribution|
+=============================+===============+=============================+===========================+
| "True" secondaries          | ❌            | ✅                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Elastically backscattered   | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Inelastically backscattered | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Total                       | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+

Definitions
-----------

Emission energy distribution is given by:

.. math::

   f(E_\mathrm{SE}) = 2 \sqrt{\frac{E_\mathrm{SE}}{\pi T^3}} \mathrm{e}^{-E_\mathrm{SE}/T}


:math:`T` is the distribution temperature in :unit:`eV`.
In order to set it's maximum to unity, we scale it by its maximum, at :math:`E_\mathrm{SE} = T/2`.

Model parameters
----------------

The parameters list is dynamically created here: :py:mod:`Maxwellian API documentation<.maxwellian>`.

To-do list
----------

.. todo::
   - Allow fitting on several distribution files with different |PE| energy.
   - Consistent input files with Chung Everhart. SEs or all?
