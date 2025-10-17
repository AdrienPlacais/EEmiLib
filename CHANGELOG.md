# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.0.x]

## [0.0.7] -- unreleased

### Added

- Support for the different flavors of Vaughan: CST, SPARK3D.
  - To recheck!
- Implemented Sombrin TEEY model.
- Implemented Chung and Everhart SEs emission energy model.

### Changed

- Defined optional dependencies.
  Use `pip install -e .[test]` to support testing.
- Doc on [ReadTheDocs](https://eemilib.readthedocs.io/en/docs-rtd/index.html)

### Fixed

- Trying to plot non-existent/not implemented data does not raise an Error anymore.

## TODO

- N. Fil criteria to evaluate fit quality.
- Allow Chung Everhart fit on several files.
- Fix: trying to plot missing data seems to create a new figure.
- ? Show some characteristics on the plot. To help debug, help user understand
  what the code understands from his data.
  - Position of Ec1, Emax, Ec2 for TEEY
  - Position of peaks for emission energy
- ? Data correction for Deesse loader.
- Plots:
  - Fix ylabel
  - Fix Legend entries
  - Different colors for different populations
  - Fix energy/angle box in GUI
  - Make energy/angle box values adjust to the interval of loaded data
  - Make data to plot/population to plot follow according to nature of model
    <!-- ## [0.0.0] 1312-01-01 -->
    <!---->
    <!-- ### Added -->
    <!---->
    <!-- ### Changed -->
    <!---->
    <!-- ### Deprecated -->
    <!---->
    <!-- ### Removed -->
    <!---->
    <!-- ### Fixed -->
    <!---->
    <!-- ### Security -->
