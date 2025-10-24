# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

# [0.0.x]

## [0.0.15] -- 2025-10-24

### Added

- `Model.display_parameters` method to log current parameters values.
- Animation in `README` to showcase GUI.
- New installation instructions adapted to PyPI.

## [0.0.14] -- 2025-10-22

### Fixed

- Should be released on PyPI.

## [0.0.13] -- 2025-10-22

### Changed

- Release on tags.

## [0.0.12] -- 2025-10-22

### Fixed

- Release should work with appropriate script.

## [0.0.11] -- 2025-10-22

### Added

- EEmiLib is now available on PyPI. Installation instructions are simpler,
  simply run

  ```bash
  pip install EEmiLib
  ```

## [0.0.10] -- 2025-10-22

### Fixed

- Release workflow works without error.

## [0.0.9]

### Added

- EEmiLib is now available on (Test)PyPI.

## [0.0.8] -- 2025-10-21

### Fixed

- Typo in dependencies.

## [0.0.7] -- 2025-10-21

### Added

- Support for the different flavors of Vaughan: CST, SPARK3D.
  - To recheck!
- Implemented Sombrin TEEY model.
- Implemented Chung and Everhart SEs emission energy model.
- Better plots:
  - Correct y-labels.
  - Correct legend entries.
- Easier GUI:
  - Loading data autofill plotting energy/angle ranges.
  - Selecting model autofill emission data type and population to plot.

### Changed

- Defined optional dependencies.
  Use `pip install -e .[test]` to support testing.
- Doc on [ReadTheDocs](https://eemilib.readthedocs.io/en/docs-rtd/index.html)

### Fixed

- Trying to plot non-existent/not implemented data does not cause the GUI to
  crash anymore.
- Display of `Parameter` units in GUI and doc.

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
