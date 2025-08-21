"""
knitout_interpreter: A comprehensive library for interpreting knitout files.

This package provides tools for parsing, validating, and executing knitout files
used to control automatic V-Bed knitting machines. It includes support for the
complete Knitout specification v2 created by McCann et al.

The library bridges the gap between high-level knitting pattern descriptions and
machine-level execution, providing comprehensive analysis and simulation capabilities.

Core Functionality:
    - run_knitout(): Simple function to parse and execute knitout files
    - Knitout_Executer: Advanced class for detailed analysis and execution control

For specialized functionality, import from submodules:
    - knitout_interpreter.knitout_operations: Individual instruction types
    - knitout_interpreter.knitout_language: Parsing and grammar support
    - knitout_interpreter.knitout_execution_structures: Execution data structures
"""
