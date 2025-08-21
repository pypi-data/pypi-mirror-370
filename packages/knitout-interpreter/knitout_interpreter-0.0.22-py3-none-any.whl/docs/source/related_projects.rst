Related Projects
================

📚 Project Ecosystem
---------------------

CMU Textiles Lab Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~

The knitout-interpreter builds upon foundational work from Carnegie Mellon University's Textiles Lab:

**knitout** - Original Specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Repository**: `knitout <https://github.com/textiles-lab/knitout>`_
- **Description**: Original knitout specification and reference tools
- **Created by**: McCann et al.
- **Purpose**: Defines the standard format for automatic knitting machine programming

The original knitout project established the specification that this interpreter implements,
providing the foundation for machine-readable knitting instructions.

**knitout-frontend-js** - JavaScript Tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Repository**: `knitout-frontend-js <https://github.com/textiles-lab/knitout-frontend-js>`_
- **Description**: JavaScript frontend tools for knitout generation
- **Language**: JavaScript/TypeScript
- **Purpose**: Web-based tools for creating and manipulating knitout files

This project provides complementary browser-based tools for working with knitout files,
offering a different ecosystem for web applications.

Core Knitting Libraries
~~~~~~~~~~~~~~~~~~~~~~~

**knit-graphs** |knit_graphs_version|
   Knitting graph data structures and analysis tools.

   - **Purpose**: Models fabric topology and stitch relationships
   - **Key Features**: Stitch dependency tracking, fabric analysis, pattern validation
   - **Integration**: Used by KnitScript to represent generated fabric structures
   - **Repository**: `knit-graphs on PyPI <https://pypi.org/project/knit-graphs/>`_

**knit-script** |vkm_version|
   A simulation of a knitting machine.

   - **Purpose**: Used to verify knitting operations and construct knit graphs.
   - **Repository**: `virtual-knitting-machine on PyPI <https://pypi.org/project/virtual-knitting-machine/>`_

**knit-script** |ks_version|
   A general purpose machine knitting langauge

   - **Purpose**: Fully programmatic support to control knitting machines.
   - **Repository**: `knit-script on PyPI <https://pypi.org/project/knit-script/>`_

**knitout-interpreter** |knitout_interp_version|
   Knitout processing and execution framework.

   - **Purpose**: Processes and validates knitout instruction files
   - **Key Features**: Instruction parsing, carriage pass organization, error detection
   - **Integration**: Processes KnitScript's generated knitout output
   - **Repository**: `knitout-interpreter on PyPI <https://pypi.org/project/knitout-interpreter/>`

Optimization and Analysis Tools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**koda-knitout** |koda_version|
   Optimization framework for knitout instructions.

   - **Purpose**: Optimizes knitout files for faster execution and better quality
   - **Key Features**: Carriage pass optimization, instruction reordering, resource minimization
   - **Integration**: Can post-process KnitScript's generated knitout for optimization
   - **Repository**: `koda-knitout on PyPI <https://pypi.org/project/koda-knitout/>`_

.. |knit_graphs_version| image:: https://img.shields.io/pypi/v/knit-graphs.svg
   :target: https://pypi.org/project/knit-graphs/

.. |ks_version| image:: https://img.shields.io/pypi/v/knit-script.svg
   :target: https://pypi.org/project/knit-script/

.. |vkm_version| image:: https://img.shields.io/pypi/v/virtual-knitting-machine.svg
   :target: https://pypi.org/project/virtual-knitting-machine/

.. |knitout_interp_version| image:: https://img.shields.io/pypi/v/knitout-interpreter.svg
   :target: https://pypi.org/project/knitout-interpreter/

.. |koda_version| image:: https://img.shields.io/pypi/v/koda-knitout.svg
   :target: https://pypi.org/project/koda-knitout/


Academic Publications
^^^^^^^^^^^^^^^^^^^^^

Key papers that have shaped this work:

- **"A Compiler for 3D Machine Knitting"** - McCann et al.
- **"Automatic Machine Knitting of 3D Meshes"** - Narayanan et al.
- **"Visual Knitting Machine Programming"** - McCann et al.
