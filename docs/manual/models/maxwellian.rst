Maxwellian distribution
=======================

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This is a model for emission energy distribution of |SEs|.
It does not take into account incidence angle of |PEs|.

.. seealso::
   :ref:`This example script <sphx_glr_auto_examples_plot_maxwellian.py>` shows
   how this model can be used in a script.

Input files
-----------

You must provide an emission energy distribution at normal incidence.
Currently, the fitting on several emission distribution files at different |PE|
energies is not supported.

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
In order to set it's maximum to unity, we scale it by its maximum, at
:math:`E_\mathrm{SE} = T/2`.

Model parameters
----------------

The parameters list is dynamically created here: :py:mod:`Maxwellian API
documentation<.maxwellian>`.
