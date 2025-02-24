EEmiLib
=======

EEmiLib (Electron EMIssion Library) holds several electron emission models and offers a simple way to fit the on electron emission data.
It is focused on electron emission models for multipactor simulation, *i.e.* for impinging energies ranging from few eV to several hundreds of eV.

Two types of outputs can be generated:
- Text files holding the different emission yields at different impact angles/impact energies.
- Electron emission models parameters.

This project is still under development.
I maintain this project on my free time, but I'll do my best to answer to any question you may have.

Scope
=====

Low-energies (multipactor)
Discrimination of secondary, backscattered

Installation
============

1. Clone the repository:
`git clone git@github.com:AdrienPlacais/EEmiLib.git`
2. Navigate to the `EEmiLib` dir and install it with all dependencies: `pip install -e .[test]`
    - Depending on your bash, you may have to enclose `.[test]` with `"`.
3. Test that everything is working with `pytest -m "not implementation"`

Notes/todo
==========

* [ ] Would be interesting to handle error bars too.
* [ ] Control on interpolation of loaded experimental data.
* [ ] Possibility to smoothen measured data?
* [ ] Show some measurables to evaluate a model quality. Nicolas Fil criterions in particular.
