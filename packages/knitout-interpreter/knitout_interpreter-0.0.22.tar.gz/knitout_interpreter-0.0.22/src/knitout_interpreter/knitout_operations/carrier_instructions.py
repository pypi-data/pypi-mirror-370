"""Knitout Operations that involve the yarn inserting system"""
from __future__ import annotations

import warnings

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_warnings.carrier_operation_warnings import (
    Mismatched_Releasehook_Warning,
)
from virtual_knitting_machine.knitting_machine_warnings.Yarn_Carrier_System_Warning import (
    Out_Inactive_Carrier_Warning,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import (
    Machine_Knit_Yarn,
)

from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
    Knitout_Instruction_Type,
)


class Yarn_Carrier_Instruction(Knitout_Instruction):
    def __init__(self, instruction_type: Knitout_Instruction_Type, carrier: int | Yarn_Carrier, comment: None | str):
        super().__init__(instruction_type, comment)
        self._carrier: int | Yarn_Carrier = carrier

    @property
    def carrier(self) -> int | Yarn_Carrier:
        """
        Returns:
            int | Yarn_Carrier: The carrier of the instruction.
        """
        return self._carrier

    @property
    def carrier_id(self) -> int:
        """
        Returns:
            int: The id of the carrier of the instruction.
        """
        return int(self._carrier)

    def __str__(self) -> str:
        return f"{self.instruction_type} {self.carrier_id}{self.comment_str}"

    def get_yarn(self, machine: Knitting_Machine) -> Machine_Knit_Yarn:
        """Get the yarn on the specified carrier.

        Args:
            machine: The knitting machine to get yarn from.

        Returns:
            The yarn on the specified carrier on the given machine.
        """
        return self.get_carrier(machine).yarn

    def get_carrier(self, machine: Knitting_Machine) -> Yarn_Carrier:
        """Get the yarn carrier specified on the given machine.

        Args:
            machine: The knitting machine to get the carrier from.

        Returns:
            The yarn carrier specified on the given machine.
        """
        return machine.carrier_system[self.carrier_id]


class Hook_Instruction(Yarn_Carrier_Instruction):

    def __init__(self, instruction_type: Knitout_Instruction_Type, carrier: int | Yarn_Carrier, comment: None | str):
        super().__init__(instruction_type, carrier, comment)


class In_Instruction(Yarn_Carrier_Instruction):

    def __init__(self, carrier: int | Yarn_Carrier, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.In, carrier, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        machine_state.bring_in(self.carrier_id)
        return True

    @staticmethod
    def execute_in(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> In_Instruction:
        """Execute an 'in' instruction to bring a carrier into the knitting area.

        Args:
            machine_state: The current machine model to update.
            carrier: The carrier to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = In_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Inhook_Instruction(Hook_Instruction):

    def __init__(self, carrier_set: Yarn_Carrier | int, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Inhook, carrier_set, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        machine_state.in_hook(self.carrier_id)
        return True

    @staticmethod
    def execute_inhook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Inhook_Instruction:
        """Execute an 'inhook' instruction to hook a carrier into position.

        Args:
            machine_state: The current machine model to update.
            carrier: The carrier to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Inhook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Releasehook_Instruction(Hook_Instruction):

    def __init__(self, carrier: int | Yarn_Carrier, comment: None | str = None, preferred_release_direction: Carriage_Pass_Direction | None = None):
        super().__init__(Knitout_Instruction_Type.Releasehook, carrier, comment)
        self._preferred_release_direction = preferred_release_direction

    @property
    def preferred_release_direction(self) -> Carriage_Pass_Direction:
        """Get the preferred direction to release this carrier.

        Returns:
            The preferred direction to release this carrier in.
            Will default to leftward release.
        """
        if self._preferred_release_direction is None:
            return Carriage_Pass_Direction.Leftward
        return self._preferred_release_direction

    def execute(self, machine_state: Knitting_Machine) -> bool:
        if machine_state.carrier_system.inserting_hook_available:
            warnings.warn(Mismatched_Releasehook_Warning(self.carrier_id))
            return False
        elif self.carrier_id != machine_state.carrier_system.hooked_carrier.carrier_id:
            warnings.warn(Mismatched_Releasehook_Warning(self.carrier_id))
        machine_state.release_hook()
        return True

    @staticmethod
    def execute_releasehook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Releasehook_Instruction:
        """Execute a 'releasehook' instruction to release a hooked carrier.

        Args:
            machine_state: The current machine model to update.
            carrier: The carrier to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Releasehook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Out_Instruction(Yarn_Carrier_Instruction):

    def __init__(self, carrier: int | Yarn_Carrier, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Out, carrier, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        machine_state.out(self.carrier_id)
        return True

    @staticmethod
    def execute_out(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Out_Instruction:
        """Execute an 'out' instruction to move a carrier out of the knitting area.

        Args:
            machine_state: The current machine model to update.
            carrier: The carrier to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Out_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction


class Outhook_Instruction(Hook_Instruction):

    def __init__(self, carrier_set: Yarn_Carrier | int, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Outhook, carrier_set, comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        carrier = machine_state.carrier_system[self.carrier_id]
        if not carrier.is_active:
            warnings.warn(Out_Inactive_Carrier_Warning(self.carrier_id))
            return False
        machine_state.out_hook(self.carrier_id)
        return True

    @staticmethod
    def execute_outhook(machine_state: Knitting_Machine, carrier: int | Yarn_Carrier, comment: str | None = None) -> Outhook_Instruction:
        """Execute an 'outhook' instruction to hook a carrier out of position.

        Args:
            machine_state: The current machine model to update.
            carrier: The carrier to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Outhook_Instruction(carrier, comment)
        instruction.execute(machine_state)
        return instruction
