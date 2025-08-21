Dependencies
============

📋 Package Dependencies
------------------------

Runtime Dependencies
~~~~~~~~~~~~~~~~~~~~~

The following packages are automatically installed with knitout-interpreter:

**Core Dependencies**

- **python** >= 3.11 - Modern Python version with latest type hinting features
- **parglare** ~0.18 - Parser generator library for processing knitout grammar
- **knit-graphs** ~0.0.6 - Knitting graph data structures for fabric representation
- **virtual-knitting-machine** ~0.0.13 - Virtual machine simulation engine
- **importlib_resources** 6.5.2 - Resource management for accessing grammar files

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

For development work, additional packages are available through the ``[dev]`` extra:

**Code Quality Tools**

- **mypy** ^1.5.0 - Static type checker for catching type errors
- **pre-commit** ^3.4.0 - Git hook framework for automated code quality checks

**Testing Framework**

- **coverage** ^7.3.0 - Coverage measurement for unittest
- **unittest-xml-reporting** ^3.2.0 - XML test reporting for CI/CD integration

**Security and Validation**

- **twine** ^4.0.0 - Package validation and PyPI upload tool

**Documentation**

- **sphinx** ^7.1.0 - Documentation generator
- **sphinx-rtd-theme** ^1.3.0 - Read the Docs theme for professional documentation
- **myst-parser** ^2.0.0 - Markdown support for Sphinx documentation

**Development Tools**

- **ipython** ^8.14.0 - Enhanced interactive Python shell for development

**Platform-Specific**

- **colorama** ^0.4.6 - Colored terminal output (Windows only)

Dependency Details
~~~~~~~~~~~~~~~~~~

Core Library Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^

**parglare** - Parser Generator
  Used for parsing knitout files according to the formal grammar specification.
  Provides robust error handling and syntax validation.

**knit-graphs** - Fabric Representation
  Provides data structures for representing the final knitted fabric structure.
  Enables analysis of loop relationships and fabric topology.

**virtual-knitting-machine** - Machine Simulation
  Simulates the behavior of V-bed knitting machines during pattern execution.
  Tracks machine state, detects errors, and validates knitting operations.

**importlib_resources** - Resource Access
  Provides access to packaged grammar files and other resources across
  different Python versions and installation methods.

Version Compatibility
~~~~~~~~~~~~~~~~~~~~~

**Python Version Support**

- **Minimum**: Python 3.11
- **Maximum**: Python 3.13 (exclusive)
- **Recommended**: Python 3.12 for best performance

**Operating System Support**

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, CentOS 8+, etc.)

**Architecture Support**

- ✅ x86_64 (64-bit Intel/AMD)
- ✅ ARM64 (Apple Silicon, ARM-based systems)


Getting Help
~~~~~~~~~~~~

If you encounter dependency issues:

1. Check the `issue tracker <https://github.com/mhofmann-Khoury/knitout_interpreter/issues>`_
2. Review the installation documentation
3. Ensure you meet all system requirements
4. Try installing in a fresh virtual environment
