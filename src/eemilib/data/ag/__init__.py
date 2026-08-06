"""Ag |TEEY| and emission distribution.

Measurements performed at ONERA, Toulouse, France using the DEESSE test
facility from 2018-05-28 to 2018-06-04.

This is an Ag sample that was heated at 200 celsius during 2 hours. It is
called "heated Ag#1" in my PhD :cite:`Placais2021`. Two types of measurements
are available:

- Emission yield at different incidence angles. Can be loaded using
  :class:`.loader.PandasLoader`.
- Emission energy data at normal incidence. Corrected using M. Villemant
  procedure :cite:`Villemant2018`. Can be loaded using
  :class:`.loader.PandasLoader`.

If you need to want to use this data in your work, please contact me first.

.. todo::
   Proper licensing, make available on Zenodo.

"""
