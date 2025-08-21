# knitout-interpreter

[![PyPI - Version](https://img.shields.io/pypi/v/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/knitout-interpreter.svg)](https://pypi.org/project/knitout-interpreter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: MyPy](https://img.shields.io/badge/type_checker-mypy-blue.svg)](https://mypy-lang.org/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A comprehensive Python library for interpreting and executing knitout files used to control automatic V-Bed knitting machines.
This library provides full support for the [Knitout specification](https://textiles-lab.github.io/knitout/knitout.html) created by McCann et al.,
enabling programmatic knitting pattern analysis, validation, and execution simulation.

## 📑 Table of Contents

- [🧶 Overview](#-overview)
- [🚀 Key Features](#-key-features)
- [📦 Installation](#-installation)
- [📚 Core Components](#-core-components)
  - [Knitout Executer](#knitout-executer)
  - [Instruction Types](#instruction-types)
  - [Carriage Pass Organization](#carriage-pass-organization)
- [📖 Examples](#-examples)
- [📋 Dependencies](#-dependencies)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📚 Related Projects](#-related-projects)
- [🔗 Links](#-links)

## 🧶 Overview

The knitout-interpreter bridges the gap between high-level knitting pattern descriptions and machine-level execution. It provides tools for:

- **Parsing** knitout files into structured Python objects
- **Validating** knitting instructions against common errors
- **Simulating** execution on virtual knitting machines
- **Analyzing** patterns for timing, width requirements, and complexity
- **Reorganizing** instructions for optimal machine execution

## 🚀 Key Features

### Core Functionality
- ✅ Full compliance with Knitout specification v2
- ✅ Support for all needle operations (knit, tuck, split, drop, xfer, miss, kick)
- ✅ Carrier management (in, out, inhook, outhook, releasehook)
- ✅ Racking and positioning controls
- ✅ Header processing (machine, gauge, yarn, carriers, position)

### Advanced Analysis
- 📊 **Execution Time Analysis**: Measure knitting time in carriage passes
- 📏 **Width Calculation**: Determine required needle bed width
- 🔍 **Error Detection**: Identify common knitting errors before execution
- 📈 **Knit Graph Generation**: Create structured representations of the final fabric

### Virtual Machine Integration
- 🖥️ Built on the [virtual-knitting-machine](https://pypi.org/project/virtual-knitting-machine/) library
- 🧠 Maintains complete machine state during execution
- 📋 Tracks loop creation, movement, and removal from the machine bed
- ⚠️ Provides detailed warnings for potential issues

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install knitout-interpreter
```

### From Source
```bash
git clone https://github.com/mhofmann-Khoury/knitout_interpreter.git
cd knitout_interpreter
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/mhofmann-Khoury/knitout_interpreter.git
cd knitout_interpreter
pip install -e ".[dev]"
pre-commit install
```

### From Test-PyPi
If you wish to install an unstable release from test-PyPi, note that this will have dependencies on PyPi repository.
Use the following command to gather those dependencies during install.
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ knitout-interpreter
```
## 🏃‍♂️ Quick Start

### Basic Usage

```python
"""Example Run of Knitout processed into instruction, final machine state, and resulting knit_graph"""
from knitout_interpreter.run_knitout import run_knitout

# Parse and execute a knitout file
instructions, machine, knit_graph = run_knitout("pattern.k")

print(f"Executed {len(instructions)} instructions")
```

### Advanced Analysis with Knitout Executer

```python
""" Example of parsing knitout lines from the knitout parser and organizing the executed instructions with the Knitout Executer."""
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
```

## 📚 Core Components

### Knitout Executer
The main analysis class that provides comprehensive execution simulation:

```python
"""Example of loading a fully specified Knitout Executer"""
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

# Parse knitout file
parsed_instructions = parse_knitout("example.k", pattern_is_file=True)

executer = Knitout_Executer(
    instructions=parsed_instructions,
    knitting_machine=Knitting_Machine(),
    accepted_error_types=[],  # Optional: Knitting Machine Errors to ignore
    knitout_version=2
)
```

**Key Properties:**
- `execution_time`: Number of carriage passes that will be executed
- `left_most_position` / `right_most_position`: The range of needle positions in the executed file.
- `carriage_passes`: List of carriage passes in the order they are executed.
- `resulting_knit_graph`: Final fabric structure

### Instruction Types

The library supports all knitout operations as Python classes:

#### Needle Operations
- `Knit_Instruction`: Create new loops, stitch through the old one.
- `Tuck_Instruction`: Create new loops, keeping old ones.
- `Split_Instruction`: Creates a loop on first specified needle while moving existing loops to the second specified needle.
- `Drop_Instruction`: Remove loops from needles
- `Xfer_Instruction`: Transfer loops between needles
- `Miss_Instruction`: Position carriers without forming loops
- `Kick_Instruction`: Specialized miss for kickbacks

#### Carrier Operations
- `In_Instruction` / `Out_Instruction`: Move carriers in/out of knitting area
- `Inhook_Instruction` / `Outhook_Instruction`: Move carriers in/out of knitting area using yarn-inserting hook.
- `Releasehook_Instruction`: Release carriers on the yarn-inserting hook.

#### Machine Control
- `Rack_Instruction`: Set bed alignment and all-needle mode.
- `Pause_Instruction`: Pause machine execution.

#### Header Declarations
- `Machine_Header_Line`: Specify machine type.
- `Gauge_Header_Line`: Set machine gauge.
- `Yarn_Header_Line`: Define yarn properties.
- `Carriers_Header_Line`: Configure available carriers.
- `Position_Header_Line`: Set knitting position.

### Carriage Pass Organization

The library automatically organizes instructions into carriage passes:

```python
"""Example of what information can be gathered from carriage passes in the knitout execution."""
from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

# Parse knitout file
parsed_instructions = parse_knitout("example.k", pattern_is_file=True)

executer = Knitout_Executer(
    instructions=parsed_instructions,
    knitting_machine=Knitting_Machine(),
    accepted_error_types=[],  # Optional: Knitting Machine Errors to ignore
    knitout_version=2
)

for carriage_pass in executer.carriage_passes:
    print(f"Pass direction: {carriage_pass.direction}")
    print(f"Instructions: {len(carriage_pass)}")
    print(f"Needle range: {carriage_pass.carriage_pass_range()}")
    print(f"Carriers used: {carriage_pass.carrier_set}")
```

## 📖 Examples

### Example 1: Basic Stockinette

```python
"""Example of loading basic stockinette knitout from a string."""
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout

knitout_code = """
;!knitout-2
;;Machine: SWG091N2
;;Gauge: 15
;;Yarn-5: 50-50 Rust
;;Carriers: 1 2 3 4 5 6 7 8 9 10
;;Position: Right
inhook 1;
tuck + f1 1;
tuck + f2 1;
tuck + f3 1;
tuck + f4 1;
knit - f4 1
knit - f3 1
knit - f2 1
knit - f1 1
knit + f1 1;
knit + f2 1;
knit + f3 1;
knit + f4 1;
knit - f4 1
knit - f3 1
knit - f2 1
knit - f1 1
releasehook 1;
outhook 1;
"""

instructions = parse_knitout(knitout_code)
# Process instructions...
```

### Example 2: Pattern Analysis

```python
"""Basic example of loading a pattern from a knitout file and analysing it."""
from knitout_interpreter.run_knitout import run_knitout
from knitout_interpreter.knitout_execution import Knitout_Executer

# Load complex pattern
instructions, machine, graph = run_knitout("complex_pattern.knitout")

# Analyze with executer
executer = Knitout_Executer(instructions, machine)

# Print analysis
print("=== Pattern Analysis ===")
print(f"Total instructions: {len(instructions)}")
print(f"Execution time: {executer.execution_time} passes")
print(f"Width: {executer.right_most_position - executer.left_most_position + 1} needles")

# Analyze carriage passes
for i, cp in enumerate(executer.carriage_passes):
    print(f"Pass {i+1}: {cp}")
```

## 📋 Dependencies

### Runtime Dependencies
- `python` >= >=3.11,<3.13
- `parglare` ^0.18 - Parser generator for knitout grammar
- `knit-graphs` ^0.0.6 - Knitting graph data structures
- `virtual-knitting-machine` ^0.0.13 - Virtual machine simulation
- `importlib_resources` ^6.5. - Resource management

### Development Dependencies
- `mypy` - Static type checking
- `pre-commit` - Code quality hooks
- `coverage` - Test coverage measurement
- `sphinx` - Documentation generation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **McCann et al.** for creating the [Knitout specification](https://textiles-lab.github.io/knitout/knitout.html)
- **Northeastern University ACT Lab** for supporting this research
- This work has been supported by the following NSF Grants:
  - 2341880: HCC:SMALL:Tools for Programming and Designing Interactive Machine-Knitted Smart Textiles
  - 2327137: Collaborative Research: HCC: Small: End-User Guided Search and Optimization for Accessible Product Customization and Design

## 📚 Related Projects

- Prior work by the CMU Textiles Lab:
  - [knitout](https://github.com/textiles-lab/knitout) - Original knitout specification and tools
  - [knitout-frontend-js](https://github.com/textiles-lab/knitout-frontend-js) - JavaScript knitout frontend
- Related Knitting Libraries from the Northeastern Act Lab
  - [knit-graphs](https://pypi.org/project/knit-graphs/) - Knitting graph data structures
  - [virtual-knitting-machine](https://pypi.org/project/virtual-knitting-machine/) - Virtual machine simulation
  - [koda-knitout](https://pypi.org/project/koda-knitout/) - Optimization framework for knitout instructions


## 🔗 Links

- **PyPI Package**: https://pypi.org/project/knitout-interpreter
- **Documentation**: https://github.com/mhofmann-Khoury/knitout_interpreter#readme
- **Issue Tracker**: https://github.com/mhofmann-Khoury/knitout_interpreter/issues

---

**Made with ❤️ by the Northeastern University ACT Lab**
