"""Module containing the Kick_Instruction class."""

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_interpreter.knitout_operations.needle_instructions import Miss_Instruction


class Kick_Instruction(Miss_Instruction):
    """A subclass of the Miss_Instruction used to mark kickbacks added in dat-complication process."""

    def __init__(self, position: int | Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set | None = None, comment: None | str = None):
        """Initialize a kick instruction for a specific needle position.

        Args:
            position: The needle position for the kickback (must be between 0 and 540).
            direction: The direction of the carriage pass.
            cs: The yarn carrier set to use. Defaults to None.
            comment: Optional comment for the instruction. Defaults to None.

        Raises:
            AssertionError: If position is not between 0 and 540.
        """
        if isinstance(position, Needle):
            self._position: int = position.position
        else:
            self._position: int = position
        assert 0 <= self.position, f"Cannot add a kickback beyond the bounds of the needle bed at position {position}"
        super().__init__(needle=Needle(is_front=True, position=position), direction=direction, cs=cs, comment=comment)

    @property
    def position(self) -> int:
        """
        Returns:
            The position from the front bed to kick the carrier to.
        """
        return self._position

    @property
    def no_carriers(self) -> bool:
        """Check if this is a soft-miss kickback with no carriers.

        Returns:
            True if this is a soft-miss kickback with no carriers.
            No carriers can be set with a null carrier set or a carrier
            set with a 0 carrier (not a valid index for a carrier).
        """
        return self.carrier_set is None or 0 in self.carrier_set.carrier_ids

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Position the carrier above the given front-bed needle position.

        Args:
            machine_state: The machine state to update.

        Returns:
            True indicating the operation completed successfully.
        """
        self._test_operation()
        assert 0 <= self.position <= machine_state.needle_count, f"Cannot add a kickback beyond the bounds of the needle bed at position {self.position}"
        machine_state.miss(self.carrier_set, self.needle, self.direction)
        return True

    @staticmethod
    def execute_kick(machine_state: Knitting_Machine,
                     needle: Needle | int, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None) -> Miss_Instruction:
        """Execute a kick instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle or front-bed needle position to move the carrier set to.
            direction: The direction to execute in.
            cs: The yarn carriers set to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Kick_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction
