"""Needle operations"""
from __future__ import annotations

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine
from virtual_knitting_machine.knitting_machine_exceptions.Needle_Exception import (
    Misaligned_Needle_Exception,
)
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier import (
    Yarn_Carrier,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Loop import (
    Machine_Knit_Loop,
)
from virtual_knitting_machine.machine_constructed_knit_graph.Machine_Knit_Yarn import (
    Machine_Knit_Yarn,
)

from knitout_interpreter.knitout_operations.knitout_instruction import (
    Knitout_Instruction,
    Knitout_Instruction_Type,
)


class Needle_Instruction(Knitout_Instruction):
    """
    The base class for all instructions that execute on a needle.

    Attributes:
        made_loops (list[Machine_Knit_Loop]): The list of loops that were made by this instruction.
        moved_loops (list[Machine_Knit_Loop]): The list of loops that transferred by this instruction.
        dropped_loops (list[Machine_Knit_Loop]): The list of loops that dropped by this instruction.
    """
    def __init__(self, instruction_type: Knitout_Instruction_Type,
                 needle: Needle, direction: None | str | Carriage_Pass_Direction = None, needle_2: None | Needle = None,
                 carrier_set: None | Yarn_Carrier_Set = None,
                 comment: None | str = None):
        super().__init__(instruction_type, comment, interrupts_carriage_pass=False)
        self._carrier_set: None | Yarn_Carrier_Set = carrier_set
        self._needle_2: None | Needle = needle_2
        if direction is not None and isinstance(direction, str):
            direction = Carriage_Pass_Direction.get_direction(direction)
        self._direction: None | Carriage_Pass_Direction = direction
        self._needle: Needle = needle
        self.made_loops: list[Machine_Knit_Loop] = []
        self.moved_loops: list[Machine_Knit_Loop] = []
        self.dropped_loops: list[Machine_Knit_Loop] = []

    @property
    def carrier_set(self) -> None | Yarn_Carrier_Set:
        """
        Returns:
            Yarn_Carrier_Set | None: The carrier set used by this instruction or None if it does not involve carriers.
        """
        return self._carrier_set

    @property
    def needle_2(self) -> None | Needle:
        """
        Returns:
            Needle | None: The needle that loops are transferred to or None if this instruction does not involve transfers.
        """
        return self._needle_2

    @property
    def direction(self) -> None | Carriage_Pass_Direction:
        """
        Returns:
            Carriage_Pass_Direction | None: The direction used by this instruction or None if this is a xfer instruction that can happen in any direction.
        """
        return self._direction

    @property
    def needle(self) -> Needle:
        """
        Returns:
            Needle: The needle that this operation executes on.
        """
        return self._needle

    def get_yarns(self, knitting_machine: Knitting_Machine) -> dict[int, Machine_Knit_Yarn]:
        """Get the yarns currently active on the carriers.

        Args:
            knitting_machine: The knitting machine to access yarn data from.

        Returns:
            Dictionary mapping carrier IDs to the yarn that is currently active on them.
        """
        return {cid: carrier.yarn for cid, carrier in self.get_carriers(knitting_machine).items()}

    def get_carriers(self, knitting_machine: Knitting_Machine) -> dict[int, Yarn_Carrier]:
        """Get the carriers currently active for this instruction.

        Args:
            knitting_machine: The knitting machine to access carrier data from.

        Returns:
            Dictionary mapping carrier IDs to the carrier objects that are currently active.
        """
        if self.carrier_set is None:
            return {}
        else:
            return {cid: knitting_machine.carrier_system[cid] for cid in self.carrier_set.carrier_ids}

    @property
    def has_second_needle(self) -> bool:
        """Check if this instruction has a second needle.

        Returns:
            True if it has a second needle.
        """
        return self.needle_2 is not None

    @property
    def has_direction(self) -> bool:
        """Check if this instruction has a direction value.

        Returns:
            True if it has a direction value.
        """
        return self.direction is not None

    @property
    def has_carrier_set(self) -> bool:
        """Check if this instruction has a carrier set.

        Returns:
            True if it has a carrier set.
        """
        return self.carrier_set is not None

    @property
    def implied_racking(self) -> None | int:
        """Get the racking required for this operation.

        Returns:
            None if no specific racking is required, or the required racking
            value to complete this operation.
        """
        if self.has_second_needle:
            return int(Knitting_Machine.get_transfer_rack(self.needle, self.needle_2))
        else:
            return None

    def _test_operation(self) -> None:
        """Test if the operation has all required parameters."""
        if self.instruction_type.directed_pass:
            assert self.has_direction, f"Cannot {self.instruction_type} without a direction"
        if self.instruction_type.requires_second_needle:
            assert self.has_second_needle, f"Cannot {self.instruction_type} without target needle"
        if self.instruction_type.requires_carrier:
            assert self.has_carrier_set, f"Cannot {self.instruction_type} without a carrier set"

    def __str__(self) -> str:
        if self.has_direction:
            dir_str = f" {self.direction}"
        else:
            dir_str = ""
        if self.has_second_needle:
            n2_str = f" {self.needle_2}"
        else:
            n2_str = ""
        if self.has_carrier_set:
            cs_str = f" {self.carrier_set}"
        else:
            cs_str = ""
        return f"{self.instruction_type}{dir_str} {self.needle}{n2_str}{cs_str}{self.comment_str}"


class Loop_Making_Instruction(Needle_Instruction):
    """Base class for instructions that create loops."""

    def __init__(self, instruction_type: Knitout_Instruction_Type,
                 needle: Needle, direction: None | str | Carriage_Pass_Direction = None,
                 needle_2: None | Needle = None,
                 carrier_set: Yarn_Carrier_Set = None,
                 comment: None | str = None):
        super().__init__(instruction_type, needle, direction, needle_2, carrier_set, comment)


class Knit_Instruction(Loop_Making_Instruction):
    """Instruction for knitting a loop on a needle."""

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Knit, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        self._test_operation()
        self.dropped_loops, self.made_loops = machine_state.knit(self.carrier_set, self.needle, self.direction)
        return True  # true even if loops is empty because the prior loops are dropped.

    @staticmethod
    def execute_knit(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None) -> Knit_Instruction:
        """Execute a knit instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            direction: The direction to execute in.
            cs: The yarn carriers set to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Knit_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Tuck_Instruction(Loop_Making_Instruction):
    """Instruction for tucking yarn on a needle without dropping existing loops."""

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Tuck, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        self._test_operation()
        self.made_loops = machine_state.tuck(self.carrier_set, self.needle, self.direction)
        return len(self.made_loops) > 0

    @staticmethod
    def execute_tuck(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None) -> Tuck_Instruction:
        """Execute a tuck instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            direction: The direction to execute in.
            cs: The yarn carriers set to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Tuck_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Split_Instruction(Loop_Making_Instruction):
    """Instruction for splitting a loop between two needles."""

    def __init__(self, needle: Needle, direction: Carriage_Pass_Direction, n2: Needle, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Split, needle, direction=direction, needle_2=n2, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        self._test_operation()
        aligned_needle = machine_state.get_aligned_needle(self.needle)
        if aligned_needle != self.needle_2:
            raise Misaligned_Needle_Exception(self.needle, self.needle_2)
        self.made_loops, self.moved_loops = machine_state.split(self.carrier_set, self.needle, self.direction)
        return len(self.made_loops) > 0 or len(self.moved_loops) > 0

    @staticmethod
    def execute_split(machine_state: Knitting_Machine,
                      needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, n2: Needle,
                      comment: str | None = None) -> Split_Instruction:
        """Execute a split instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            direction: The direction to execute in.
            cs: The yarn carriers set to execute with.
            n2: The second needle to execute to.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Split_Instruction(needle, direction, n2, cs, comment)
        instruction.execute(machine_state)
        return instruction


class Drop_Instruction(Needle_Instruction):
    """Instruction for dropping loops from a needle."""

    def __init__(self, needle: Needle, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Drop, needle, comment=comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        self._test_operation()
        self.dropped_loops = machine_state.drop(self.needle)
        return True

    @staticmethod
    def execute_Drop(machine_state: Knitting_Machine,
                     needle: Needle, comment: str | None = None) -> Drop_Instruction:
        """Execute a drop instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Drop_Instruction(needle, comment)
        instruction.execute(machine_state)
        return instruction


class Xfer_Instruction(Needle_Instruction):
    """Instruction for transferring loops between needles."""

    def __init__(self, needle: Needle, n2: Needle, comment: None | str = None, record_location: bool = True):
        super().__init__(Knitout_Instruction_Type.Xfer, needle, needle_2=n2, comment=comment)
        self.record_location: bool = record_location
        self.loop_crossings_made: dict[Machine_Knit_Loop, list[Machine_Knit_Loop]] = {}  # Todo: Use loop crossing code.

    def add_loop_crossing(self, left_loop: Machine_Knit_Loop, right_loop: Machine_Knit_Loop) -> None:
        """Update loop crossing to show transfers crossing loops.

        Args:
            left_loop: The left loop involved in the crossing.
            right_loop: The right loop involved in the crossing.
        """
        if left_loop not in self.loop_crossings_made:
            self.loop_crossings_made[left_loop] = []
        self.loop_crossings_made[left_loop].append(right_loop)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        self._test_operation()
        assert isinstance(self.needle_2, Needle)
        to_slider = self.needle_2.is_slider
        aligned_needle = machine_state.get_aligned_needle(self.needle, aligned_slider=to_slider)
        if aligned_needle != self.needle_2:
            raise Misaligned_Needle_Exception(self.needle, self.needle_2)
        self.moved_loops = machine_state.xfer(self.needle, to_slider=to_slider)
        return len(self.moved_loops) > 0

    @staticmethod
    def execute_xfer(machine_state: Knitting_Machine,
                     needle: Needle, n2: Needle,
                     comment: str | None = None) -> Xfer_Instruction:
        """Execute a transfer instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            n2: The second needle to execute to.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Xfer_Instruction(needle, n2, comment)
        instruction.execute(machine_state)
        return instruction


class Miss_Instruction(Needle_Instruction):
    """Instruction for positioning carriers above a needle without forming loops."""

    def __init__(self, needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set, comment: None | str = None):
        super().__init__(Knitout_Instruction_Type.Miss, needle, direction=direction, carrier_set=cs, comment=comment)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Position the carrier above the given needle.

        Args:
            machine_state: The machine state to update.

        Returns:
            True indicating the operation completed successfully.
        """
        self._test_operation()
        machine_state.miss(self.carrier_set, self.needle, self.direction)
        return True

    @staticmethod
    def execute_miss(machine_state: Knitting_Machine,
                     needle: Needle, direction: str | Carriage_Pass_Direction, cs: Yarn_Carrier_Set,
                     comment: str | None = None) -> Miss_Instruction:
        """Execute a miss instruction on the machine.

        Args:
            machine_state: The current machine model to update.
            needle: The needle to execute on.
            direction: The direction to execute in.
            cs: The yarn carriers set to execute with.
            comment: Additional details to document in the knitout.

        Returns:
            The instruction that was executed.
        """
        instruction = Miss_Instruction(needle, direction, cs, comment)
        instruction.execute(machine_state)
        return instruction
