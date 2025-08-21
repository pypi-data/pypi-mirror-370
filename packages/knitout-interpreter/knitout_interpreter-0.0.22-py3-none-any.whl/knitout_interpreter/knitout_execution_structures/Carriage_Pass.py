"""Module containing the Carriage Pass class."""
from __future__ import annotations

import time
from typing import Iterator, cast

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction_Type,
)
from knitout_interpreter.knitout_operations.Knitout_Line import (
    Knitout_Comment_Line,
    Knitout_Line,
)
from knitout_interpreter.knitout_operations.needle_instructions import (
    Needle_Instruction,
    Xfer_Instruction,
)
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction


class Carriage_Pass:
    """Manages knitout operations that are organized in a single carriage pass.

    Attributes:
        all_needle_rack (bool): True if this carriage pass is set to allow all needle racking.
        rack (int): The offset racking alignment for the carriage pass.
    """

    def __init__(self, first_instruction: Needle_Instruction, rack: int, all_needle_rack: bool):
        """Initialize a new carriage pass with the first instruction.

        Args:
            first_instruction: The first needle instruction in this carriage pass.
            rack: The rack position for this carriage pass.
            all_needle_rack: Whether this pass uses all-needle racking.
        """
        self._creation_time: float = time.time()
        self.all_needle_rack: bool = all_needle_rack
        self.rack: int = rack
        self._xfer_pass: bool = isinstance(first_instruction, Xfer_Instruction)
        if self._xfer_pass:
            self._carrier_set: Yarn_Carrier_Set | None = None
            self._direction: Carriage_Pass_Direction | None = None
        else:
            self._carrier_set: Yarn_Carrier_Set | None = first_instruction.carrier_set
            self._direction: Carriage_Pass_Direction | None = first_instruction.direction
        self._instructions: list[Needle_Instruction] = [first_instruction]
        self._needles_to_instruction: dict[Needle, Needle_Instruction] = {first_instruction.needle: first_instruction}
        self._instruction_types_to_needles: dict[Knitout_Instruction_Type, dict[Needle, Needle_Instruction]] = {first_instruction.instruction_type:
                                                                                                                    {first_instruction.needle: first_instruction}}

    @property
    def carrier_set(self) -> Yarn_Carrier_Set | None:
        """
        Returns:
            Yarn_Carrier_Set | None: The carrier set used in this carriage pass or None if the pass does not involve carriers.
        """
        return self._carrier_set

    @property
    def xfer_pass(self) -> bool:
        """
        Returns:
            bool: True if this carriage pass is transfer operations.
        """
        return self._xfer_pass

    def instruction_set(self) -> set[Needle_Instruction]:
        """Get an unordered set of the instructions in the carriage pass.

        Returns:
            An unordered set of the instructions in the carriage pass.
        """
        return set(self._instructions)

    def rightward_sorted_needles(self) -> list[Needle]:
        """Get needles sorted from left to right.

        Returns:
            List of needles in the carriage pass sorted from left to right.
        """
        return cast(list[Needle], Carriage_Pass_Direction.Rightward.sort_needles(self._needles_to_instruction.keys(), self.rack))

    def leftward_sorted_needles(self) -> list[Needle]:
        """Get needles sorted from right to left.

        Returns:
            List of needles in the carriage pass sorted from right to left.
        """
        return cast(list[Needle], Carriage_Pass_Direction.Leftward.sort_needles(self._needles_to_instruction.keys(), self.rack))

    def sorted_needles(self) -> list[Needle]:
        """Get needles sorted by carriage pass direction.

        Returns:
            List of needles in carriage pass sorted by direction of carriage pass
            or from left to right if no direction is given.
        """
        if self.direction is None:
            return self.rightward_sorted_needles()
        else:
            return cast(list[Needle], self.direction.sort_needles(self._needles_to_instruction.keys(), self.rack))

    def instructions_by_needles(self, needles: list[Needle]) -> list[Needle_Instruction]:
        """Get instructions ordered by the given needle list.

        Args:
            needles: Ordered list of needles involved in the carriage pass.

        Returns:
            The ordered set of instructions that start from the given needles.
        """
        return [self._needles_to_instruction[n] for n in needles]

    def carriage_pass_range(self) -> tuple[int, int]:
        """Get the leftmost and rightmost needle positions in the carriage pass.

        Returns:
            Tuple of (leftmost position, rightmost position) in the carriage pass.
        """
        sorted_needles = self.rightward_sorted_needles()
        return int(sorted_needles[0].racked_position_on_front(rack=self.rack)), int(sorted_needles[-1].racked_position_on_front(rack=self.rack))

    def rack_instruction(self, comment: str = "Racking for next carriage pass.") -> Rack_Instruction:
        """Create a racking instruction to set up this carriage pass.

        Args:
            comment: Comment to include with the racking instruction.

        Returns:
            Racking instruction to set up this carriage pass.
        """
        return Rack_Instruction.rack_instruction_from_int_specification(self.rack, self.all_needle_rack, comment)

    @property
    def direction(self) -> Carriage_Pass_Direction | None:
        """Get or set the direction of the carriage pass.

        Setting the direction will reorder the instructions to the given direction.
        Should only be used to reorder Xfer Passes.

        Returns:
            The direction of the carriage pass.
        """
        return self._direction

    @direction.setter
    def direction(self, direction: Carriage_Pass_Direction) -> None:
        """Set the direction of the carriage pass.

        Args:
            direction: The new direction for the carriage pass.
        """
        self._direction = direction
        sorted_needles = self.needles
        self._instructions = [self._needles_to_instruction[n] for n in sorted_needles]

    @property
    def needles(self) -> list[Needle]:
        """Get needles in the order given by instruction set.

        Returns:
            Needles in order given by instruction set.
        """
        needles = [i.needle for i in self._instructions]
        if self.direction is not None:
            return cast(list[Needle], self.direction.sort_needles(needles, self.rack))
        else:
            return needles  # needles in order of given instructions

    @property
    def first_instruction(self) -> Needle_Instruction:
        """Get the first instruction given to carriage pass.

        Returns:
            First instruction given to carriage pass.
        """
        return self._instructions[0]

    @property
    def last_instruction(self) -> Needle_Instruction:
        """Get the last instruction executed in the carriage pass.

        Returns:
            Last instruction executed in the given carriage pass.
        """
        return self._instructions[-1]

    @property
    def last_needle(self) -> Needle:
        """Get the needle at the end of the ordered instructions.

        Returns:
            Needle at the end of the ordered instructions.
        """
        return self.needles[-1]

    def contains_instruction_type(self, instruction_type: Knitout_Instruction_Type) -> bool:
        """Check if the carriage pass contains a specific instruction type.

        Args:
            instruction_type: Instruction type to consider.

        Returns:
            True if the instruction type is used at least once in this carriage pass.
        """
        return instruction_type in self._instruction_types_to_needles

    def add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """Attempt to add an instruction to the carriage pass.

        Args:
            instruction: The instruction to attempt to add to the carriage pass.
            rack: The required racking of this instruction.
            all_needle_rack: The all_needle racking requirement for this instruction.

        Returns:
            True if instruction was added to pass. Otherwise, False implies that
            the instruction cannot be added to this carriage pass.
        """
        if self.can_add_instruction(instruction, rack, all_needle_rack):
            self._instructions.append(instruction)
            self._needles_to_instruction[instruction.needle] = instruction
            if instruction.instruction_type not in self._instruction_types_to_needles:
                self._instruction_types_to_needles[instruction.instruction_type] = {}
            self._instruction_types_to_needles[instruction.instruction_type][instruction.needle] = instruction
            return True
        else:
            return False

    def compatible_with_pass_type(self, instruction: Needle_Instruction) -> bool:
        """Check if an instruction is compatible with this type of carriage pass.

        Args:
            instruction: The instruction to consider compatibility with.

        Returns:
            True if instruction is compatible with this type of carriage pass.
        """
        return bool(self.first_instruction.instruction_type.compatible_pass(instruction.instruction_type))

    def can_add_instruction(self, instruction: Needle_Instruction, rack: int, all_needle_rack: bool) -> bool:
        """Check if an instruction can be added to this carriage pass.

        Args:
            instruction: The instruction to consider adding to the carriage pass.
            rack: The required racking of this instruction.
            all_needle_rack: The all_needle racking requirement for this instruction.

        Returns:
            True if the instruction can be added to this carriage pass. Otherwise, False.
        """
        if rack != self.rack:
            return False
        elif all_needle_rack != self.all_needle_rack:
            return False
        elif instruction.direction != self._direction:
            return False
        elif instruction.carrier_set != self.carrier_set:
            return False
        elif not self.compatible_with_pass_type(instruction):
            return False
        elif instruction.needle in self._needles_to_instruction:  # Already has an instruction at this needle.
            return False
        elif self._direction is None:
            if instruction.needle_2 in self._needles_to_instruction:
                return False
        elif (self.all_needle_rack  # All needle rack
              and instruction.needle.is_front != self.last_needle.is_front  # last and new instruction on opposite beds
              and instruction.needle.racked_position_on_front(self.rack) == self.last_needle.racked_position_on_front(self.rack)):  # Last and new instruction at all-needle same position
            return True
        elif not self._direction.needles_are_in_pass_direction(self.last_needle, instruction.needle, self.rack, self.all_needle_rack):
            return False
        return True

    def can_merge_pass(self, next_carriage_pass: Carriage_Pass) -> bool:
        """Check if this carriage pass can be merged with the next one.

        Args:
            next_carriage_pass: A carriage pass that happens immediately after this carriage pass.

        Returns:
            True if these can be merged into one carriage pass.
        """
        if self.direction == next_carriage_pass.direction and self.compatible_with_pass_type(next_carriage_pass.first_instruction):
            next_left_needle, next_right_needle = next_carriage_pass.carriage_pass_range()
            if self.direction is Carriage_Pass_Direction.Rightward:
                return bool(self.last_needle.position < next_left_needle)
            elif self.direction is Carriage_Pass_Direction.Leftward:
                return bool(self.last_needle.position > next_right_needle)
        return False

    def merge_carriage_pass(self, next_carriage_pass: Carriage_Pass, check_compatibility: bool = False) -> bool:
        """Merge the next carriage pass into this carriage pass.

        Args:
            next_carriage_pass: A carriage pass that happens immediately after this carriage pass.
            check_compatibility: If true, checks compatibility before merging.

        Returns:
            True if the merge was successful.
        """
        if check_compatibility and not self.can_merge_pass(next_carriage_pass):
            return False
        for instruction in next_carriage_pass:
            added = self.add_instruction(instruction, next_carriage_pass.rack, next_carriage_pass.all_needle_rack)
            assert added, f'Attempted to merge {self} and {next_carriage_pass} but failed to add {instruction}.'
        return True

    def execute(self, knitting_machine: Knitting_Machine) -> list[Knitout_Line]:
        """Execute carriage pass with an implied racking operation on the given knitting machine.

        Will default to ordering xfers in a rightward ascending direction.

        Args:
            knitting_machine: The knitting machine to execute the carriage pass on.

        Returns:
            A list of executed instructions from the carriage pass.
        """
        executed_instructions = []
        rack_instruction = self.rack_instruction()
        updated = rack_instruction.execute(knitting_machine)
        if updated:
            executed_instructions.append(rack_instruction)
        if self._xfer_pass:
            self.direction = Carriage_Pass_Direction.Rightward  # default xfers to be in ascending order
        for instruction in self:
            updated = instruction.execute(knitting_machine)
            if updated:
                executed_instructions.append(instruction)
            else:
                executed_instructions.append(Knitout_Comment_Line(instruction))
        return executed_instructions

    def __str__(self) -> str:
        """Return string representation of the carriage pass.

        Returns:
            String representation showing direction, instruction types, and details.
        """
        string = ""
        indent = ""
        if not self._xfer_pass:
            string = f"in {self._direction} direction:"
            if len(self._instruction_types_to_needles) > 1:
                indent = "\t"
                string += "\n"
        for instruction_type, needles in self._instruction_types_to_needles.items():
            string += f"{indent}{instruction_type.value} {list(needles.keys())}"
        if self._xfer_pass:
            string += f" at {self.rack}"
        if self.carrier_set is not None:
            string += f" with {self.carrier_set}"
        string += "\n"
        return string

    def __list__(self) -> list[Knitout_Line]:
        """Convert carriage pass to list of knitout lines.

        Returns:
            List of knitout lines from this carriage pass.
        """
        return [*self]

    def __len__(self) -> int:
        """Get the number of instructions in the carriage pass.

        Returns:
            Number of instructions in the carriage pass.
        """
        return len(self._instructions)

    def __repr__(self) -> str:
        """Return detailed representation of the carriage pass.

        Returns:
            String representation of the internal instructions list.
        """
        return str(self._instructions)

    def __iter__(self) -> Iterator[Needle_Instruction]:
        """Iterate over the instructions in the carriage pass.

        Returns:
            Iterator over the instructions.
        """
        return iter(self._instructions)

    def __getitem__(self, item: int | slice) -> Knitout_Line | list[Knitout_Line]:
        """Get instruction(s) by index or slice.

        Args:
            item: Index or slice to retrieve.

        Returns:
            Instruction or list of instructions at the specified index/slice.
        """
        return self._instructions[item]

    def __hash__(self) -> int:
        """Get hash of the carriage pass based on creation time.

        Returns:
            Hash value based on creation time.
        """
        return hash(self._creation_time)
