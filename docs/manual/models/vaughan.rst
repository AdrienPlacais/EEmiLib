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

Under the limit :math:`E_0` (:math:`12.5\mathrm{\,eV}` by default), the TEEY is set to a unique value (:math:`0.5` by default).

.. math::

    \sigma_\mathrm{max}(\theta) = \sigma_\mathrm{max}(\theta = 0^\circ) \times \frac{1}{k_s\theta^2/\pi}

    E_\mathrm{max}(\theta) = E_\mathrm{max}(\theta = 0^\circ) \times \frac{1}{k_{se}\theta^2/\pi}

The :math:`k_s` and :math:`k_{se}` are both set to unity by default.

The factor :math:`k` is given by:

.. math::

    k &= 0.56 \mathrm{\quad if~} \xi \leq 1 \\
      &= 0.25 \mathrm{\quad if~} 1< \xi \leq 3.6 \\

Model parameters
----------------

The parameters list is dynamically created here: :py:mod:`Vaughan API documentation<.vaughan>`.

Implementations
---------------

Two alternative implementations for Vaughan are implemented: `CST` and `SPARK3D`.
Just instantiate your model with:

.. code-block:: python

   model = Vaughan(implementation="CST") # or "SPARK3D"
   # alternative:
   model = Vaughan()
   model.preset_implementation("CST")

From the GUI, manually reproduce the steps described in the :meth:`.vaughan.Vaughan.preset_implementation` method.
More specific documentation is also listed in :meth:`.vaughan.Vaughan.preset_implementation`.

Parameter Vaughan with :math:`E_{\mathrm{c,\,1}}` instead of :math:`E_0`
------------------------------------------------------------------------

When :math:`E_0` is unlocked, a fit over this variable is performed to match :math:`E_{\mathrm{c,\,1}}`.
You must provide either a TEEY file path, either enter the other Vaughan parameters yourself (see image below), and click `Fit!`.

.. image:: /manual/models/images/gui_fit_e0.png
   :target: vaughan.html
   :width: 600
   :alt: How to fit E_0
   :align: center

To-do list
----------

.. todo::
    - Unlock :math:`k_s`, :math:`k_{se}` to have better overall fit?
      In particular: if several incidence angles are provided.
    - Instructions to match CST Vaughan.
    - Instructions to match SPARK3D Vaughan.
