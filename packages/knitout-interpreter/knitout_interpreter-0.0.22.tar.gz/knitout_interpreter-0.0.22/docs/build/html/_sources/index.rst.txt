knitout-interpreter
===================

.. image:: https://img.shields.io/pypi/v/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter
   :alt: Python Version

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License

.. image:: https://img.shields.io/badge/type_checker-mypy-blue.svg
   :target: https://mypy-lang.org/
   :alt: Code style: MyPy

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: Pre-commit

A comprehensive Python library for interpreting and executing knitout files used to control automatic V-Bed knitting machines.
This library provides full support for the `Knitout specification <https://textiles-lab.github.io/knitout/knitout.html>`_ created by McCann et al.,
enabling programmatic knitting pattern analysis, validation, and execution simulation.

🧶 Overview
-----------

The knitout-interpreter bridges the gap between high-level knitting pattern descriptions and machine-level execution. It provides tools for:

- **Parsing** knitout files into structured Python objects
- **Validating** knitting instructions against common errors
- **Simulating** execution on virtual knitting machines
- **Analyzing** patterns for timing, width requirements, and complexity
- **Reorganizing** instructions for optimal machine execution

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   installation
   quickstart
   examples
   core_components

.. toctree::
   :maxdepth: 3
   :caption: API Reference
   :hidden:

   modules

.. toctree::
   :maxdepth: 1
   :caption: Project Info
   :hidden:

   dependencies
   related_projects
   acknowledgments
