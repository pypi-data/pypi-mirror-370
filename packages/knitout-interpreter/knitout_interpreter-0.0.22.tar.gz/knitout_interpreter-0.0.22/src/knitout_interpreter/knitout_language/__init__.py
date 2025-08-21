"""
knitout_language: Parsing and grammar support for knitout files.

This module provides the parsing infrastructure for knitout files, including grammar definitions, parser actions, and execution context management.
It handles the conversion from raw knitout text files into structured Python objects thatcan be executed on virtual knitting machines.

Key Components:
    - Knitout_Parser: Main parser class using Parglare for grammar-based parsing
    - parse_knitout: Convenience function for parsing knitout files or strings
    - Knitout_Context: Manages the state and context during knitout execution
    - knitout_actions: Parser action functions that convert grammar matches to objects
    - Grammar files: <knitout.pg> and <knitout.pgt> contain the formal grammar definition

Parsing Process:
    1. Raw knitout text is tokenized according to the grammar.
    2. Parser actions convert tokens into instruction objects.
    3. Context manager organizes instructions into executable sequences.
    4. Instructions can be executed on virtual knitting machines.


Grammar Support:
    The parsing is based on a formal grammar definition that supports:
    - All knitout v2 specification instructions
    - Header declarations (machine, gauge, yarn, carriers, position)
    - Comments and version specifications
    - Proper error handling and reporting
"""
