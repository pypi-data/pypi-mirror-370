Quick Start
===========

🚀 Key Features
---------------

Core Functionality
~~~~~~~~~~~~~~~~~~
- ✅ Full compliance with Knitout specification v2
- ✅ Support for all needle operations (knit, tuck, split, drop, xfer, miss, kick)
- ✅ Carrier management (in, out, inhook, outhook, releasehook)
- ✅ Racking and positioning controls
- ✅ Header processing (machine, gauge, yarn, carriers, position)

Advanced Analysis
~~~~~~~~~~~~~~~~~
- 📊 **Execution Time Analysis**: Measure knitting time in carriage passes
- 📏 **Width Calculation**: Determine required needle bed width
- 🔍 **Error Detection**: Identify common knitting errors before execution
- 📈 **Knit Graph Generation**: Create structured representations of the final fabric

Virtual Machine Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- 🖥️ Built on the `virtual-knitting-machine <https://pypi.org/project/virtual-knitting-machine/>`_ library
- 🧠 Maintains complete machine state during execution
- 📋 Tracks loop creation, movement, and removal from the machine bed
- ⚠️ Provides detailed warnings for potential issues

🏃‍♂️ Basic Usage
-----------------

Simple Pattern Execution
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.run_knitout import run_knitout

    # Parse and execute a knitout file
    instructions, machine, knit_graph = run_knitout("pattern.k")
    print(f"Executed {len(instructions)} instructions")

Advanced Analysis with Knitout Executer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from knitout_interpreter.knitout_execution import Knitout_Executer
    from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
    from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

    # Parse knitout file
    instructions = parse_knitout("complex_pattern.k", pattern_is_file=True)

    # Execute with analysis
    executer = Knitout_Executer(instructions, Knitting_Machine())

    # Get execution metrics
    print(f"Execution time: {executer.execution_time} carriage passes")
    print(f"Width required: {executer.left_most_position} to {executer.right_most_position}")

    # Save reorganized instructions
    executer.write_executed_instructions("executed_pattern.k")
