Sombrin
=======

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This model was designed to be particularly precise on the first cross-over energy :cite:`Sombrin1993`.
Implementation is taken from :cite:`Fil2016a,Fil2020`.
It gives the TEEY, and does not take the incidence angle of PEs into account.


Input files
-----------

You must provide measured TEEY at normal incidence.

+-----------------------------+---------------+-----------------------------+---------------------------+
|                             |Emission Yield |Emission energy distribution |Emission angle distribution|
+=============================+===============+=============================+===========================+
| "True" secondaries          | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Elastically backscattered   | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Inelastically backscattered | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Total                       | ✅            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+

Definitions
-----------

The TEEY is given by:

.. math::

    \sigma(E) = \frac{
      2\sigma_\mathrm{max} \left( \frac{E}{E_\mathrm{max}} \right)^{E_\mathrm{param}}
    }{
      1 + \left( \frac{E}{E_\mathrm{max}} \right)^{2E_\mathrm{param}}
    }

:math:`E_\mathrm{param}` is defined by:

.. math::

  E_\mathrm{param} = \frac{
      \ln{\left( \sigma_\mathrm{max} - \sqrt{\sigma_\mathrm{max}^2 - 1} \right)}
    }{
      \ln{\left( \frac{E_\mathrm{c,\,1}}{E_\mathrm{max}}\right)}
    }

Model parameters
----------------

The parameters list is dynamically created here: :py:mod:`Sombrin API documentation<.sombrin>`.

