"""
knitout_execution_structures: Data structures for organizing knitout execution.

This module provides specialized data structures that organize knitout instructions into meaningful execution units.
These structures bridge the gap between individual knitout instructions and the actual execution patterns on knitting machines.

Key Concepts:
    Carriage Pass: A sequence of instructions that can be executed in a single pass of the knitting machine carriage.
     Instructions in a carriage pass share common properties like direction, racking, and carrier usage.

    Organization: Instructions are automatically grouped into carriage passes based on machine constraints and execution efficiency.
    This organization is crucial for accurate timing analysis and machine operation.

Core Components:
    - Carriage_Pass: Main data structure representing a carriage pass
    - Pass organization and merging logic
    - Execution timing and analysis capabilities
    - Needle range and width calculations

Machine Execution Model:
    Real knitting machines operate in carriage passes rather than individual instructions.
    A carriage pass represents one sweep of the carriage across the needle bed, during which multiple operations can occur simultaneously.
"""
