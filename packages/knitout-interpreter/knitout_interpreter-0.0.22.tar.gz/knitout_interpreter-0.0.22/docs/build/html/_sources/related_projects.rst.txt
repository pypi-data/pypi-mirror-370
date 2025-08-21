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

Northeastern ACT Lab Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following projects form an integrated ecosystem for computational knitting research:

**knit-graphs** - Fabric Data Structures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **PyPI**: `knit-graphs <https://pypi.org/project/knit-graphs/>`_
- **Description**: Knitting graph data structures and algorithms
- **Integration**: Used by knitout-interpreter for fabric representation
- **Features**:
  - Loop relationship modeling
  - Fabric topology analysis
  - Stitch pattern representation
  - Graph-based fabric operations

.. code-block:: python

    from knit_graphs.Knit_Graph import Knit_Graph
    from knitout_interpreter.run_knitout import run_knitout

    # The knit graph is automatically generated
    instructions, machine, knit_graph = run_knitout("pattern.k")
    print(f"Graph has {knit_graph.node_count} nodes")

**virtual-knitting-machine** - Machine Simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **PyPI**: `virtual-knitting-machine <https://pypi.org/project/virtual-knitting-machine/>`_
- **Description**: Virtual V-bed knitting machine simulation
- **Integration**: Core dependency for knitout-interpreter execution
- **Features**:
  - Complete machine state tracking
  - Error detection and validation
  - Loop management and transfer
  - Carriage movement simulation

.. code-block:: python

    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from knitout_interpreter.knitout_execution import Knitout_Executer

    machine = Knitting_Machine()
    executer = Knitout_Executer(instructions, machine)

**koda-knitout** - Optimization Framework
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **PyPI**: `koda-knitout <https://pypi.org/project/koda-knitout/>`_
- **Description**: Optimization framework for knitout instructions
- **Purpose**: Automated optimization of knitting patterns for efficiency
- **Features**:
  - Instruction sequence optimization
  - Carriage pass minimization
  - Yarn usage optimization
  - Performance analysis tools

This project complements knitout-interpreter by providing optimization capabilities
for the patterns that the interpreter can execute and analyze.

Related Research Areas
~~~~~~~~~~~~~~~~~~~~~~

Computational Fabrication
^^^^^^^^^^^^^^^^^^^^^^^^^^

The knitout ecosystem contributes to the broader field of computational fabrication:

- **Digital manufacturing** through automated knitting
- **Parametric design** for customized textile products
- **Algorithm-driven fabrication** processes
- **Human-computer interaction** in craft and making

Academic Publications
^^^^^^^^^^^^^^^^^^^^^

Key papers that have shaped this work:

- **"A Compiler for 3D Machine Knitting"** - McCann et al.
- **"Automatic Machine Knitting of 3D Meshes"** - Narayanan et al.
- **"Visual Knitting Machine Programming"** - McCann et al.

Integration Examples
~~~~~~~~~~~~~~~~~~~~

Using Multiple Projects Together
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Complete workflow using the full ecosystem
    from knitout_interpreter.run_knitout import run_knitout
    from knitout_interpreter.knitout_execution import Knitout_Executer
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
    from knit_graphs.Knit_Graph import Knit_Graph

    # Execute pattern and get all components
    instructions, machine, knit_graph = run_knitout("pattern.k")

    # Detailed analysis
    executer = Knitout_Executer(instructions, machine)

    # Access integrated results
    print(f"Execution time: {executer.execution_time} passes")
    print(f"Machine state: {machine.active_needle_count} active needles")
    print(f"Fabric structure: {knit_graph.node_count} stitches")

Community and Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Research Community
^^^^^^^^^^^^^^^^^^^

These projects serve the computational textiles research community:

- **Academic researchers** in HCI, fabrication, and textiles
- **Industry practitioners** in digital knitting
- **Students and educators** in computational design
- **Makers and artists** exploring digital craft

Contributing to the Ecosystem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ways to contribute to the broader project ecosystem:

1. **Report issues** and bugs across projects
2. **Suggest features** for improved integration
3. **Contribute code** to any of the component libraries
4. **Share examples** and use cases
5. **Write documentation** and tutorials

**GitHub Organizations**:
- CMU Textiles Lab: `@textiles-lab <https://github.com/textiles-lab>`_
- Northeastern ACT Lab: Projects under individual maintainer accounts

Future Directions
~~~~~~~~~~~~~~~~~

The ecosystem continues to evolve with:

- **Enhanced optimization algorithms** in koda-knitout
- **Expanded machine support** in virtual-knitting-machine
- **Advanced graph operations** in knit-graphs
- **Improved parsing capabilities** in knitout-interpreter
- **Integration with CAD tools** and design software
- **Support for new knitting techniques** and machine types
