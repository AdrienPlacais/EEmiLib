.. _furman-pivi-link:

Furman and Pivi
===============

.. toctree::
   :maxdepth: 4
   :hidden:

Presentation
------------

This model :cite:`Furman2002,Furman2013` provides the emission yield for |SEs|,
|EBEs| and |IBEs|, as well as their emission energy distributions. Emission
angle distributions are to be implemented. It takes the incidence anngle and
energy of |PEs| into account. This is a phenomenological and mathematically
consistent model, but its parameters do not necessarily have a physical
meaning.

.. seealso::
   :ref:`This example script <sphx_glr_auto_examples_plot_furman_pivi.py>`
   shows how this model can be used in a script.

Input files
-----------

This model needs experimental |TEEY| at several incidence angles as well as
emission energy distribution measurements.

.. note::
   When |TEEY| and measured energy distribution are loaded, energy distribution
   is automatically re-scaled so that its integral for every |PE| energy
   matches corresponding |TEEY|. This behaviour is controlled by
   :class:`.DataMatrix` and is mandatory for the fitting to work.

   This operation is performed when calling :meth:`.DataMatrix.load_data` if the
   `rescale_energy_distributions_to_teey` argument is set to ``True`` (the
   default). Internally, the
   :meth:`.DataMatrix._rescale_energy_distributions_to_teey` is called.

+-----------------------------+---------------+-----------------------------+---------------------------+
|                             |Emission Yield |Emission energy distribution |Emission angle distribution|
+=============================+===============+=============================+===========================+
| "True" secondaries          | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Elastically backscattered   | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Inelastically backscattered | ❌            | ❌                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+
| Total                       | ✅            | ✅                          | ❌                        |
+-----------------------------+---------------+-----------------------------+---------------------------+

Definitions
-----------

For a complete definition of the model, see the associated modules:

   - :mod:`.furman_pivi.se` for |SEs| (or "true" secondaries),
   - :mod:`.furman_pivi.ebe` for |EBEs| (or "reflected" electrons),
   - :mod:`.furman_pivi.ibe` for |IBEs| (or "rediffused" electrons).


Model parameters
----------------

The (long) parameters list is dynamically created here: :mod:`Furman and Pivi
API documentation<.furman_pivi.furman_pivi>`.

Implementations
---------------

Following Furman and Pivi paper :cite:`Furman2002`, several implementations of
the model can be used, influencing the |SEEY|.


|SEs| distribution
^^^^^^^^^^^^^^^^^^

For a given |SEEY|, the actual number of emitted |SEs| can follow a Poisson or
Binomial law. This is controlled by choosing respectively `distribution =
"Poisson"` or `distribution = "Binomial"`.

Probability normalization
^^^^^^^^^^^^^^^^^^^^^^^^^

- With `normalization = "incident"`, the probability to emit ``n`` electrons
  for a given |SEEY| is calculated directly from the |SEEY|.

  - See Eqs. (35)/(36) in Ref. :cite:`Furman2002`.

- With `normalization = "penetrated"`, the probability to emit ``n`` electrons
  is calculated from the |SEEY| and corrected with the |EBEEY| and |IBEEY|. It
  corrects the fact that the |PEs| that already generate |EBEs| or |IBEs|
  cannot also generate |SEs|.

  - See Eqs. (39) to (46) in Ref. :cite:`Furman2002`.

GUI
^^^

Select your implementation from the `Implementations` menu.

API
^^^

Instantiate your model with:

.. code-block:: python

   model = FurmanPivi(distribution="Poisson", normalization="incident")
   # alternative:
   model = FurmanPivi()
   model.set_implementation("distribution", "Binomial")
   model.set_implementation("normalization", "penetrated")

More specific documentation in :meth:`.model.FurmanPivi.set_implementation`.

To-do list
----------

.. todo::
   - Store the max number of secondaries in the Model, make it editable, like
     from the Implementations section in the GUI.

      .. warning::
         This would influence number of mandatory :math:`\epsilon_i` and
         :math:`p_i` parameters. This is a significant refactor. And it would
         not be very useful -- except for niche use cases... So this is not
         prioritary.

   - Warning when |SEEY| exceeds max number of |SEs|
     :data:`.M_MAX_SECONDARIES`.
   - Implement emission angle distributions.
   - Raise warning or error when there are no measurements at oblique incidence
     angle.
   - Also document parameter name changes here.
   - The FP fit in the example is not very good. In particular for the energy
     distributions. Can we do better?
