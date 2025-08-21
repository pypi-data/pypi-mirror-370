"""Module for the Pause Knitting Machine Instruction"""
from __future__ import annotations

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine

from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
    Knitout_Instruction_Type,
)


class Pause_Instruction(Knitout_Instruction):
    """Instruction for pausing the knitting machine."""

    def __init__(self, comment: None | str = None):
        """Initialize a pause instruction.

        Args:
            comment: Optional comment for the pause instruction.
        """
        super().__init__(Knitout_Instruction_Type.Pause, comment, interrupts_carriage_pass=True)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the pause instruction.

        Args:
            machine_state: The machine state (not modified by pause).

        Returns:
            False as no update is caused by pauses.
        """
        return False  # No Update caused by pauses

    @staticmethod
    def execute_pause(machine_state: Knitting_Machine, comment: str | None = None) -> Pause_Instruction:
        """Execute a pause instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Pause_Instruction(comment)
        instruction.execute(machine_state)
        return instruction
