Vaughan
=======

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This is the most basic Vaughan model, as defined in original Vaughan paper :cite:`Vaughan1989,Vaughan1993`.
It gives the TEEY, and takes the incidence angle of PEs into account.


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

    \sigma(E, \theta) &= \sigma_\mathrm{max}(\theta) \times (\xi \mathrm{e}^{1-\xi} )^k \mathrm{\quad if~} \xi \leq 3.6 \\
                      &= \sigma_\mathrm{max}(\theta) \times \frac{1.125}{\xi^{0.35}} \mathrm{\quad if~} \xi > 3.6

:math:`\xi` is defined by:

.. math::

    \xi = \frac{E - E_0}{E_\mathrm{max} - E_0}

Under the limit :math:`E_0` (:math:`12.5\mathrm{\,eV}` by default), the TEEY is
set to a unique value (:math:`0.5` by default).

.. todo::
    Releasing :math:`E_0` constraint to fit :math:`E_{c,\,1}`.

.. math::

    \sigma_\mathrm{max}(\theta) = \sigma_\mathrm{max}(\theta = 0^\circ) \times \frac{1}{k_s\theta^2/\pi}

    E_\mathrm{max}(\theta) = E_\mathrm{max}(\theta = 0^\circ) \times \frac{1}{k_{se}\theta^2/\pi}

The :math:`k_s` and :math:`k_{se}` are both set to unity by default.

.. todo::
    Should be locked by default, but possibility to release their constraints
    to allow fit?


The factor :math:`k` is given by:

.. math::

    k &= 0.56 \mathrm{\quad if~} \xi \leq 1 \\
      &= 0.25 \mathrm{\quad if~} 1< \xi \leq 3.6 \\

Model parameters
----------------

The list of the parameters is dynamically created in the :py:mod:`Vaughan API documentation<.vaughan>`.

Bibliography
------------
.. bibliography::

.. todo::
    - Unlock :math:`E_0` to fit :math:`E_{c,\,1}`.
    - Unlock :math:`k_s`, :math:`k_{se}` to have better overall fit?
    - Instructions to match CST Vaughan.
    - Instructions to match SPARK3D Vaughan.
