"""Module containing the knitout executer class"""
from knit_graphs.Knit_Graph import Knit_Graph
from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_execution_structures.Carriage_Pass import Carriage_Pass
from knitout_interpreter.knitout_operations.Header_Line import (
    Knitout_Header_Line,
    Knitting_Machine_Header,
)
from knitout_interpreter.knitout_operations.Knitout_Line import (
    Knitout_Comment_Line,
    Knitout_Line,
    Knitout_Version_Line,
)
from knitout_interpreter.knitout_operations.needle_instructions import (
    Needle_Instruction,
)
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction


class Knitout_Executer:
    """A class used to execute a set of knitout instructions on a virtual knitting machine.
    Attributes:
        knitting_machine (Knitting_Machine): Knitting Machine instance being executed on.
        instructions (list[Knitout_Line]): Instructions to execute.
        process (list[Knitout_Line | Carriage_Pass]): The ordered list of knitout lines and carriage passes executed.
        executed_header (Knitting_Machine_Header): The header that creates this knitting machine.
        executed_instructions (list[Knitout_Line]): The instructions that executed and updated the knitting machine state.

    """

    def __init__(self, instructions: list[Knitout_Line], knitting_machine: Knitting_Machine | None = None, accepted_error_types: list | None = None, knitout_version: int = 2):
        """Initialize the knitout executer.

        Args:
            instructions: List of knitout instructions to execute.
            knitting_machine: The virtual knitting machine to execute instructions on.
            accepted_error_types: List of exception types that can be resolved by
                commenting them out. Defaults to None.
            knitout_version: The knitout version to use. Defaults to 2.
        """
        self._knitout_version = knitout_version
        if accepted_error_types is None:
            accepted_error_types = []
        if knitting_machine is None:
            knitting_machine = Knitting_Machine()
        self.knitting_machine: Knitting_Machine = knitting_machine
        self.instructions: list[Knitout_Line] = instructions
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_header: Knitting_Machine_Header = Knitting_Machine_Header(self.knitting_machine.machine_specification)
        self.executed_instructions: list[Knitout_Line] = []
        self.test_and_organize_instructions(accepted_error_types)
        self._carriage_passes: list[Carriage_Pass] = [cp for cp in self.process if isinstance(cp, Carriage_Pass)]
        self._left_most_position: int | None = None
        self._right_most_position: int | None = None
        for cp in self._carriage_passes:
            left, right = cp.carriage_pass_range()
            if self._left_most_position is None:
                self._left_most_position = left
            elif left is not None:
                self._left_most_position = min(self._left_most_position, left)
            if self._right_most_position is None:
                self._right_most_position = right
            elif right is not None:
                self._right_most_position = max(self._right_most_position, right)

    @property
    def knitout_version(self) -> int:
        """
        Returns:
            int: The knitout version being executed.
        """
        return self._knitout_version

    @property
    def version_line(self) -> Knitout_Version_Line:
        """Get the version line for the executed knitout.

        Returns:
            The version line for the executed knitout.
        """
        return Knitout_Version_Line(self.knitout_version)

    @property
    def execution_time(self) -> int:
        """Get the execution time as measured by carriage passes.

        Returns:
            Count of carriage passes in process as a measure of knitting time.
        """
        return len(self._carriage_passes)

    @property
    def left_most_position(self) -> int | None:
        """Get the leftmost needle position used in execution.

        Returns:
            The position of the left most needle used in execution, or None if
            no needles were used.
        """
        return self._left_most_position

    @property
    def right_most_position(self) -> int | None:
        """Get the rightmost needle position used in execution.

        Returns:
            The position of the right most needle used in the execution, or None
            if no needles were used.
        """
        return self._right_most_position

    @property
    def resulting_knit_graph(self) -> Knit_Graph:
        """Get the knit graph resulting from instruction execution.

        Returns:
            Knit Graph that results from execution of these instructions.
        """
        return self.knitting_machine.knit_graph

    @property
    def carriage_passes(self) -> list[Carriage_Pass]:
        """Get the carriage passes from this execution.

        Returns:
            The carriage passes resulting from this execution in execution order.
        """
        return self._carriage_passes

    def test_and_organize_instructions(self, accepted_error_types: list | None = None) -> None:
        """Test the given execution and organize the instructions in the class structure.

        This method processes all instructions, organizing them into carriage passes
        and handling any errors that occur during execution.

        Args:
            accepted_error_types: A list of exceptions that instructions may throw
                that can be resolved by commenting them out. Defaults to None.
        """
        if accepted_error_types is None:
            accepted_error_types = []
        self.process: list[Knitout_Line | Carriage_Pass] = []
        self.executed_instructions: list[Knitout_Line] = []
        in_header = not self.knitting_machine.knit_graph.has_loop  # If the prior machine state already had a knit graph, then the header cannot modify the machine state.
        current_pass = None
        for instruction in self.instructions:
            try:
                if instruction.interrupts_carriage_pass:
                    in_header = False
                if isinstance(instruction, Needle_Instruction):
                    in_header = False
                    if current_pass is None:  # Make a new Carriage Pass from this
                        current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                    else:  # Check if instruction can be added to the carriage pass, add it or create a new current carriage pass
                        was_added = current_pass.add_instruction(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                        if not was_added:
                            executed_pass = current_pass.execute(self.knitting_machine)
                            self.process.append(current_pass)
                            self.executed_instructions.extend(executed_pass)
                            current_pass = Carriage_Pass(instruction, self.knitting_machine.rack, self.knitting_machine.all_needle_rack)
                elif isinstance(instruction, Knitout_Version_Line):
                    self._knitout_version = instruction.version
                elif isinstance(instruction, Knitout_Header_Line):
                    updated = self.executed_header.update_header(instruction, update_machine=in_header)  # only update the machine_state if in the header section
                    if updated:
                        self.knitting_machine = Knitting_Machine(self.executed_header.specification)
                else:
                    if instruction.interrupts_carriage_pass and current_pass is not None:  # interrupt the current carriage pass with rack and carrier operations
                        executed_pass = current_pass.execute(self.knitting_machine)
                        self.process.append(current_pass)
                        self.executed_instructions.extend(executed_pass)
                        current_pass = None
                    updated = instruction.execute(self.knitting_machine)
                    if updated or isinstance(instruction, Pause_Instruction):
                        self.process.append(instruction)
                        self.executed_instructions.append(instruction)
                    else:
                        comment = Knitout_Comment_Line(instruction)  # create a no-op comment for this line because it did not cause an update.
                        self.process.append(comment)
                        self.executed_instructions.append(comment)
            except tuple(accepted_error_types) as e:
                error_comment = Knitout_Comment_Line(f"Excluded {type(e).__name__}: {e.message}")
                self.process.append(error_comment)
                self.executed_instructions.append(error_comment)
                comment = Knitout_Comment_Line(instruction)
                self.process.append(comment)
                self.executed_instructions.append(comment)
        if current_pass is not None:
            executed_pass = current_pass.execute(self.knitting_machine)
            self.process.append(current_pass)
            self.executed_instructions.extend(executed_pass)
        # add the header and version line to the beginning of the executed instructions
        executed_process = self.executed_instructions
        self.executed_instructions = self.executed_header.get_header_lines(self.knitout_version)
        self.executed_instructions.extend(executed_process)

    def write_executed_instructions(self, filename: str) -> None:
        """Write a file with the organized knitout instructions.

        Args:
            filename: The file path to write the executed instructions to.
        """
        with open(filename, "w") as file:
            file.writelines([str(instruction) for instruction in self.executed_instructions])
