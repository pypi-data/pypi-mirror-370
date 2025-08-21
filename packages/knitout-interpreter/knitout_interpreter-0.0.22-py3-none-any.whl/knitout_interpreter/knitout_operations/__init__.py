"""
knitout_operations: Individual knitout instruction implementations.

This module contains all the instruction classes that represent individual knitout operations.
These classes implement the complete Knitout specification v2, providing Python objects for every type of instruction that can appear in a knitout file.

The instructions are organized into several categories based on their function:

Needle Operations:
    Instructions that operate on specific needles to manipulate loops and yarn.
    These form the core knitting operations and directly affect the fabric structure.

Carrier Operations:
    Instructions that manage yarn carriers - the system that supplies yarn to the knitting needles.
    These control yarn insertion and removal.

Machine Control:
    Instructions that control machine state, including bed alignment (racking), execution pauses, and other machine-level operations.

Header Declarations:
    Special instructions that appear at the beginning of knitout files to specify machine configuration, yarn properties, and other setup parameters.

Base Classes:
    Fundamental classes that provide common functionality and type definitions for all instruction types.

Instruction Execution Model:
    Each instruction class implements an execute() method that applies the instruction's effects to a virtual knitting machine state.
    This allows for simulation, validation, and analysis of knitout programs before running them on physical machines.
"""
