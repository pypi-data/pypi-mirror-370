"""Module used to manage the context of a knitout interpreter."""
from __future__ import annotations

from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution import Knitout_Executer
from knitout_interpreter.knitout_language.Knitout_Parser import parse_knitout
from knitout_interpreter.knitout_operations.Header_Line import (
    Knitout_Header_Line,
    Knitting_Machine_Header,
)
from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
)
from knitout_interpreter.knitout_operations.Knitout_Line import (
    Knitout_Comment_Line,
    Knitout_Line,
    Knitout_Version_Line,
)


def process_knitout_instructions(knitout_lines: list[Knitout_Line]) -> tuple[Knitout_Version_Line, list[Knitout_Header_Line], list[Knitout_Instruction], list[Knitout_Comment_Line]]:
    """Separate list of knitout codes into components of a program for execution.

    Args:
        knitout_lines (list[Knitout_Line]): List of knitout instructions to separate into program components.

    Returns:
        tuple[Knitout_Version_Line, list[Knitout_Header_Line], list[Knitout_Instruction], list[Knitout_Comment_Line]]:
            * Version line for the knitout program
            * List of header lines
            * List of instruction lines
            * List of comment lines
    """
    version_line: Knitout_Version_Line = Knitout_Version_Line(-1)  # -1 set to undo default if no version line is provided.
    head: list[Knitout_Header_Line] = []
    instructions: list[Knitout_Instruction] = []
    comments: list[Knitout_Comment_Line] = []
    for knitout_line in knitout_lines:
        if isinstance(knitout_line, Knitout_Version_Line):
            assert version_line.version == knitout_line.version or version_line.version < 0, f"Cannot have multiple versions of knitout {version_line} and {knitout_line}"
            version_line = knitout_line
        elif isinstance(knitout_line, Knitout_Header_Line):
            head.append(knitout_line)
        elif isinstance(knitout_line, Knitout_Instruction):
            instructions.append(knitout_line)
        elif isinstance(knitout_line, Knitout_Comment_Line):
            comments.append(knitout_line)
        else:
            assert False, f"Cannot process code {knitout_line}"
    if version_line.version < 0:
        version_line = Knitout_Version_Line(2, "Version defaulted to 2")
    return version_line, head, instructions, comments


class Knitout_Context:
    """Maintains information about the state of a knitting process as knitout instructions are executed.

    Attributes:
        machine_state (Knitting_Machine): State of the knitting machine that the context is executing on.
        executed_header (list[Knitout_Header_Line]): The ordered list of header lines that have been executed in this context.
        executed_instructions (list[Knitout_Instruction]): The ordered list of instructions executed in this context.
    """

    def __init__(self) -> None:
        self.machine_state: Knitting_Machine = Knitting_Machine()
        self._version_line: Knitout_Version_Line | None = None
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(self.machine_state.machine_specification)
        self.executed_instructions: list[Knitout_Instruction] = []

    @property
    def version(self) -> int:
        """Get the knitout version of the current context.

        Returns:
            The knitout version number, defaults to 2 if no version is set.
        """
        if self._version_line is not None:
            return int(self._version_line.version)
        else:
            return 2

    @version.setter
    def version(self, version_line: Knitout_Version_Line) -> None:
        """Set the version line for the current context.

        This will override any existing version.

        Args:
            version_line: The version line to set for this context.
        """
        self._version_line = version_line

    def execute_header(self, header_declarations: list[Knitout_Header_Line]) -> None:
        """Update the machine state based on the given header values.

        Header declarations that do not change the current context can optionally
        be converted to comments.

        Args:
            header_declarations: The header lines to update based on.
        """
        for header_line in header_declarations:
            updated = self.executed_header.update_header(header_line, update_machine=True)  # update process will always yield a complete header
            if updated:
                self.machine_state = Knitting_Machine(machine_specification=self.machine_state.machine_specification)

    def execute_instructions(self, instructions: list[Knitout_Line]) -> None:
        """Execute the instruction set on the machine state defined by the current header.

        Args:
            instructions: Instructions to execute on the knitting machine.
        """
        execution = Knitout_Executer(instructions=instructions, knitting_machine=self.machine_state, knitout_version=self.version)
        self.executed_instructions = execution.executed_instructions

    def execute_knitout(self, version_line: Knitout_Version_Line,
                        header_declarations: list[Knitout_Header_Line],
                        instructions: list[Knitout_Instruction]) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """Execute the given knitout organized by version, header, and instructions.

        Args:
            version_line: The version of knitout to use.
            header_declarations: The header to define the knitout file.
            instructions: The instructions to execute on the machine.

        Returns:
            A tuple containing:
                - List of knitout instructions that were executed
                - Machine state after execution
                - Knit graph created by execution
        """
        self.version = version_line
        self.execute_header(header_declarations)
        self.execute_instructions(instructions)
        for i, instruction in enumerate(self.executed_instructions):
            instruction.original_line_number = i
        return self.executed_instructions, self.machine_state, self.machine_state.knit_graph

    def process_knitout_file(self, knitout_file_name: str) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """Parse and process a file of knitout code.

        Args:
            knitout_file_name: File path containing knitout code to process.

        Returns:
            A tuple containing:
                - List of executed knitout lines
                - Knitting machine state after execution
                - Knit graph formed by execution
        """
        codes = parse_knitout(knitout_file_name, pattern_is_file=True, debug_parser=False, debug_parser_layout=False)
        return self.execute_knitout_instructions(codes)

    def execute_knitout_instructions(self, codes: list[Knitout_Line]) -> tuple[list[Knitout_Line], Knitting_Machine, Knit_Graph]:
        """Execute given knitout instructions.

        Args:
            codes: List of knitout lines to execute.

        Returns:
            A tuple containing:
                - List of executed knitout lines
                - Machine state after execution
                - Knit graph created by execution
        """
        version, head, instructions, comments = process_knitout_instructions(codes)
        return self.execute_knitout(version, head, instructions)
