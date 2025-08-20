# Changelog

All notable changes to this project will be documented in this file (from `0.9.14+`).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.9.16 (Unreleased)

### Added
- The new strategy ``Randomized()`` implements randomized leave-p-out (rLpO) to interpolate between existing strategies.
- Comprehensive root ``Makefile`` with 40+ development commands for unified project workflow.
- UV package manager integration for 10-100x faster dependency resolution.
  - Documentation was updated accordingly.

### Changed
- The approach to reproducibility was reworked to allow true randomness when no ``seed`` is provided in the main classes.
  - Previously, the seed was internally set to 1, preventing truly random behavior.
- Removes ``silent`` parameter from ``ExtremeConformalDetector()``, ``StandardConformalDetector()`` and ``WeightedConformalDetector()``.
  - The parameter is being replaced by more consistent logging-based progress control.
  - Documentation was updated and an example for logging configuration was added in ``examples/utils/``.
- Centralized version handling with ``nonconform/__init__.py`` as single source of truth.
- Reworked `README.md` to reflect the current scope of features.
- Migrated from pip/venv to UV package manager with lockfile for reproducible builds.
- Enhanced pre-commit configuration with UV lock file validation.
- Removed ``docs/Makefile`` and ``docs/make.bat`` in favor of unified root Makefile.
- Minor code refinements.

### Fixed
- Fixed PyTorch version constraint from `>=2.7.0` to `>=2.0.0` for broader compatibility.
- Added missing build tool dependencies (`build`, `twine`) to development dependency group.
- Cleaned up Ruff configuration inconsistencies:
  - Removed conflicting include/exclude rules for Markdown files.
  - Removed reference to non-existent `paper.bib` file from exclude patterns.
- Updated documentation to include UV installation examples alongside pip commands for consistency.
  - Both main README.md and PyPI README now show UV and pip alternatives.
  - Corrected UV command syntax to use `uv pip install` instead of `uv add` for package installation.

## 0.9.15 (2025-08-13)

### Added
- Callback for `Bootstrap()` strategy to inspect the calibration set.
  - Mainly for research purposes, this feature may monitor calibration set convergence and inform early stopping.
  - Respective usage example was added, documentation was updated accordingly.

### Changed
- Simplified building the documentation on Linux (`.docs/Makefile`) and Windows (`./docs/make.bat`).
  - On Windows, `.\make.bat` compiles to `.html`, on Linux/WSL `.\make.bat pdf` compiles to `.pdf`.
    - Mind the `[docs]` additional dependency.

### Security
- Migration to `numpy 2.x.x`
