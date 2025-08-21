Installation
============

📦 Installation Methods
------------------------

System Requirements
~~~~~~~~~~~~~~~~~~~

- **Python**: 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Architecture**: x86_64 or ARM64

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install knitout-interpreter is using pip:

.. code-block:: bash

    pip install knitout-interpreter

This will install the latest stable release from the Python Package Index along with all required dependencies.

From Source
~~~~~~~~~~~

To install from source (useful for development or getting the latest features):

.. code-block:: bash

    git clone https://github.com/mhofmann-Khoury/knitout_interpreter.git
    cd knitout_interpreter
    pip install -e .

The `-e` flag installs in "editable" mode, so changes to the source code will be reflected immediately.

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development work, install with development dependencies:

.. code-block:: bash

    git clone https://github.com/mhofmann-Khoury/knitout_interpreter.git
    cd knitout_interpreter
    pip install -e ".[dev]"
    pre-commit install

This installs additional tools for:

- Code quality checking (mypy, pre-commit)
- Testing and coverage measurement
- Documentation generation
- Security scanning

From Test-PyPI
~~~~~~~~~~~~~~~

To install unstable releases from Test-PyPI:

.. code-block:: bash

    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ knitout-interpreter

.. warning::
    Test-PyPI releases may be unstable and should only be used for testing purposes.

Getting Help
~~~~~~~~~~~~

If you continue to have installation issues:

1. Check the `GitHub Issues <https://github.com/mhofmann-Khoury/knitout_interpreter/issues>`_ page
2. Create a new issue with:
   - Your operating system and Python version
   - Complete error messages
   - Steps you've already tried
3. Contact the maintainer: m.hofmann@northeastern.edu

Next Steps
~~~~~~~~~~

After successful installation:

1. Read the :doc:`quickstart` guide
2. Try the :doc:`examples`
3. Explore the :doc:`core_components`
4. Check out the API documentation
