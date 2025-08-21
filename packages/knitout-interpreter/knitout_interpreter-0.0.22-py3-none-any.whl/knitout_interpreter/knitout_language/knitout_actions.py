"""Actions for reducing in Knitout Parser"""
from typing import Any

from parglare import get_collector
from virtual_knitting_machine.machine_components.carriage_system.Carriage_Pass_Direction import (
    Carriage_Pass_Direction,
)
from virtual_knitting_machine.machine_components.needles.Needle import Needle
from virtual_knitting_machine.machine_components.needles.Slider_Needle import (
    Slider_Needle,
)
from virtual_knitting_machine.machine_components.yarn_management.Yarn_Carrier_Set import (
    Yarn_Carrier_Set,
)

from knitout_interpreter.knitout_operations.carrier_instructions import (
    In_Instruction,
    Inhook_Instruction,
    Out_Instruction,
    Outhook_Instruction,
    Releasehook_Instruction,
)
from knitout_interpreter.knitout_operations.Header_Line import (
    Carriers_Header_Line,
    Gauge_Header_Line,
    Knitout_Header_Line,
    Machine_Header_Line,
    Position_Header_Line,
    Yarn_Header_Line,
)
from knitout_interpreter.knitout_operations.kick_instruction import Kick_Instruction
from knitout_interpreter.knitout_operations.Knitout_Line import (
    Knitout_Comment_Line,
    Knitout_Line,
    Knitout_Version_Line,
)
from knitout_interpreter.knitout_operations.needle_instructions import (
    Drop_Instruction,
    Knit_Instruction,
    Miss_Instruction,
    Split_Instruction,
    Tuck_Instruction,
    Xfer_Instruction,
)
from knitout_interpreter.knitout_operations.Pause_Instruction import Pause_Instruction
from knitout_interpreter.knitout_operations.Rack_Instruction import Rack_Instruction

action = get_collector()


@action
def comment(_: Any, __: Any, content: str | None) -> str | None:
    """Extracts the content of a comment.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        content: The content of the comment.

    Returns:
        The content of the comment.
    """
    return content


@action
def code_line(_: Any, __: Any, c: Knitout_Line | None, com: str | None) -> Knitout_Line | None:
    """Creates a knitout line with optional comment.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: The knitout line to execute, if any.
        com: The comment to append to the knitout line.

    Returns:
        The knitout line created or None if no values are given.
    """
    if c is None:
        if com is None:
            return None
        c = Knitout_Comment_Line(comment=com)
    if com is not None:
        c.comment = com
    return c


@action
def magic_string(_: Any, __: Any, v: int) -> Knitout_Version_Line:
    """Creates a knitout version line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        v: Version number.

    Returns:
        The version line knitout line.
    """
    return Knitout_Version_Line(v)


@action
def header_line(_: Any, __: Any, h_op: Knitout_Header_Line) -> Knitout_Header_Line:
    """Returns a header line operation.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        h_op: Operation on the line.

    Returns:
        The header operation.
    """
    return h_op


@action
def machine_op(_: Any, __: Any, m: str) -> Machine_Header_Line:
    """Creates a machine header line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        m: The machine name as a string.

    Returns:
        The machine declaration operation.
    """
    return Machine_Header_Line(m)


@action
def gauge_op(_: Any, __: Any, g: int) -> Gauge_Header_Line:
    """Creates a gauge header line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        g: Gauge value.

    Returns:
        Gauge_Declaration.
    """
    return Gauge_Header_Line(g)


@action
def yarn_op(_: Any, __: Any, cid: int, plies: int, weight: int, color: str) -> Yarn_Header_Line:
    """Creates a yarn header line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        cid: The carrier to assign the yarn too.
        plies: Plies in the yarn.
        weight: Weight of the yarn.
        color: The yarn color.

    Returns:
        Yarn declaration.
    """
    return Yarn_Header_Line(cid, plies, weight, color)


@action
def carriers_op(_: Any, __: Any, CS: Yarn_Carrier_Set) -> Carriers_Header_Line:
    """Creates a carriers header line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        CS: The carriers that are available.

    Returns:
        Carrier declaration.
    """
    return Carriers_Header_Line(CS)


@action
def position_op(_: Any, __: Any, p: str) -> Position_Header_Line:
    """Creates a position header line.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        p: The position of operations.

    Returns:
        The position declaration.
    """
    return Position_Header_Line(p)


@action
def in_op(_: Any, __: Any, c: int) -> In_Instruction:
    """Creates an in instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: The carrier to bring in.

    Returns:
        In operation on a carrier set.
    """
    return In_Instruction(c)


@action
def inhook_op(_: Any, __: Any, c: int) -> Inhook_Instruction:
    """Creates an inhook instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: The carrier to hook in.

    Returns:
        Inhook operation on carrier set.
    """
    return Inhook_Instruction(c)


@action
def releasehook_op(_: Any, __: Any, c: int) -> Releasehook_Instruction:
    """Creates a releasehook instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: Carrier set.

    Returns:
        Releasehook operation on carrier set.
    """
    return Releasehook_Instruction(c)


@action
def out_op(_: Any, __: Any, c: int) -> Out_Instruction:
    """Creates an out instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: Carrier set.

    Returns:
        Out operation on the carrier set.
    """
    return Out_Instruction(c)


@action
def outhook_op(_: Any, __: Any, c: int) -> Outhook_Instruction:
    """Creates an outhook instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        c: Carrier set.

    Returns:
        Outhook operation on the carrier set.
    """
    return Outhook_Instruction(c)


@action
def rack_op(_: Any, __: Any, R: float) -> Rack_Instruction:
    """Creates a rack instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        R: Rack value.

    Returns:
        Rack operation.
    """
    return Rack_Instruction(R)


@action
def knit_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Knit_Instruction:
    """Creates a knit instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        D: Direction operates in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Knit operation.
    """
    return Knit_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def tuck_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Tuck_Instruction:
    """Creates a tuck instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        D: Direction operates in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Tuck operation.
    """
    return Tuck_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def miss_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Miss_Instruction:
    """Creates a miss instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        D: Direction to operate in.
        N: Needle to operate on.
        CS: A carrier set.

    Returns:
        Miss operation.
    """
    return Miss_Instruction(N, Carriage_Pass_Direction.get_direction(D), CS)


@action
def kick_op(_: Any, __: Any, D: str, N: Needle, CS: Yarn_Carrier_Set) -> Kick_Instruction:
    """Creates a kick instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        D: The direction to operate in.
        N: The needle to position the kickback.
        CS: The carrier set to kick.

    Returns:
        The specified Kick Operation.
    """
    return Kick_Instruction(N.position, Carriage_Pass_Direction.get_direction(D), CS)


@action
def split_op(_: Any, __: Any, D: str, N: Needle, N2: Needle, CS: Yarn_Carrier_Set) -> Split_Instruction:
    """Creates a split instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        D: Direction operates in.
        N: Needle to operate on.
        N2: Second needle to move to.
        CS: A carrier set.

    Returns:
        Split operation.
    """
    return Split_Instruction(N, Carriage_Pass_Direction.get_direction(D), N2, CS)


@action
def drop_op(_: Any, __: Any, N: Needle) -> Drop_Instruction:
    """Creates a drop instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        N: Needle to drop from.

    Returns:
        Drop operation.
    """
    return Drop_Instruction(N)


@action
def xfer_op(_: Any, __: Any, N: Needle, N2: Needle) -> Xfer_Instruction:
    """Creates a transfer instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        N: Needle to transfer from.
        N2: Needle to transfer to.

    Returns:
        Xfer operation.
    """
    return Xfer_Instruction(N, N2)


@action
def pause_op(_: Any, __: Any) -> Pause_Instruction:
    """Creates a pause instruction.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.

    Returns:
        Pause operation.
    """
    return Pause_Instruction()


@action
def identifier(_: Any, node: str) -> str:
    """Returns an identifier string.

    Args:
        _: The parser element that created this value.
        node: Identifier string.

    Returns:
        The identifier string.
    """
    return node


@action
def float_exp(_: Any, node: str) -> float:
    """Converts a string to a float.

    Args:
        _: The parser element that created this value.
        node: Float string.

    Returns:
        Float conversion.
    """
    digits = ""
    for c in node:
        if c.isdigit() or c == "." or c == "-":
            digits += c
    return float(digits)


@action
def int_exp(_: Any, node: str) -> int:
    """Converts a string to an integer.

    Args:
        _: The parser element that created this value.
        node: Integer string.

    Returns:
        Integer conversion.
    """
    return int(float_exp(None, node))


@action
def needle_id(_: Any, node: str) -> Needle:
    """Creates a needle from a string representation.

    Args:
        _: The parser element that created this value.
        node: String of the given needle.

    Returns:
        The Needle represented by this string.
    """
    is_front = "f" in node
    slider = "s" in node
    num_str = node[1:]  # cut bed off
    if slider:
        num_str = node[2:]  # cut slider off
    pos = int(num_str)
    if slider:
        return Slider_Needle(is_front, pos)
    else:
        return Needle(is_front, pos)


@action
def carrier_set(_: Any, __: Any, carriers: list[int]) -> Yarn_Carrier_Set:
    """Creates a yarn carrier set.

    Args:
        _: The parser element that created this value.
        __: Unused parameter.
        carriers: Carriers in set.

    Returns:
        Carrier set.
    """
    return Yarn_Carrier_Set(carriers)
