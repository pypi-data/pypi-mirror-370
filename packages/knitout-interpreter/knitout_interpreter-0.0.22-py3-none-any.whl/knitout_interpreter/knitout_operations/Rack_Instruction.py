"""Module for the Rack_Instruction class."""
from __future__ import annotations

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
    Knitout_Instruction_Type,
)


class Rack_Instruction(Knitout_Instruction):
    """Instruction for setting the rack alignment between front and back beds."""

    def __init__(self, rack: float, comment: None | str = None):
        """Initialize a rack instruction.

        Args:
            rack: The rack value including all-needle alignment specification.
            comment: Optional comment to include with the instruction.
        """
        super().__init__(Knitout_Instruction_Type.Rack, comment)
        self._rack_value: float = rack

    @property
    def rack(self) -> int:
        """Get the integer value of rack alignment.

        Returns:
            Integer value of rack alignment.
        """
        if self.all_needle_rack and self.rack_value < 0:  # All needle racking adds .25 which changes the integer translation
            return int(self.rack_value) - 1
        else:
            return int(self.rack_value)  # remove any all needle rack modifier

    @property
    def all_needle_rack(self) -> bool:
        """Check if rack causes all-needle-knitting alignment.

        Returns:
            True if rack causes all-needle-knitting alignment.
        """
        return abs(self._rack_value - int(self._rack_value)) != 0.0

    @property
    def rack_value(self) -> float:
        """Get the rack value including all-needle-knitting alignment.

        Returns:
            The value of the rack including all-needle-knitting alignment as float specification.
        """
        return self._rack_value

    def __str__(self) -> str:
        """Return string representation of the rack instruction.

        Returns:
            String representation showing instruction type, rack value, and comment.
        """
        if not self.all_needle_rack:
            return f"{self.instruction_type} {int(self._rack_value)}{self.comment_str}"
        return f"{self.instruction_type} {self._rack_value}{self.comment_str}"

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the rack instruction on the given machine.

        Args:
            machine_state: The knitting machine to update with the rack instruction.

        Returns:
            True if the machine state was updated, False if no change was needed.
        """
        if machine_state.rack == self.rack and machine_state.all_needle_rack == self.all_needle_rack:
            return False
        machine_state.rack = self._rack_value
        return True

    @staticmethod
    def rack_instruction_from_int_specification(rack: int = 0, all_needle_rack: bool = False, comment: None | str = None) -> Rack_Instruction:
        """Create a rack instruction from integer specification.

        Note: From Knitout Specification:
        Number indicating the offset of the front bed relative to the back bed.
        That is, at racking R, back needle index B is aligned to front needle index B+R.
        Needles are considered aligned if they can transfer.
        That is, at racking 2, it is possible to transfer from f3 to b1.
        May be fractional on some machines. E.g., on Shima machines, 0.25/-0.75 are used for all-needle knitting.

        Args:
            rack: Integer racking value (default 0).
            all_needle_rack: Whether to use all-needle knitting alignment (default False).
            comment: Optional comment to include with the instruction.

        Returns:
            Rack instruction configured with the specified parameters.
        """
        rack_value: float = float(rack)
        if all_needle_rack:
            rack_value += 0.25
        return Rack_Instruction(rack_value, comment)

    @staticmethod
    def execute_rack(machine_state: Knitting_Machine, racking: float, comment: str | None = None) -> Rack_Instruction:
        """Execute a rack instruction immediately on the machine.

        Args:
            machine_state: The current machine model to update.
            racking: The new racking to set the machine to.
            comment: Additional details to document in the knitout.

        Returns:
            The racking instruction that was executed.
        """
        instruction = Rack_Instruction(racking, comment)
        instruction.execute(machine_state)
        return instruction
