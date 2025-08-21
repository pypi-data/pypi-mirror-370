"""Base class for Knitout Lines of code"""
from __future__ import annotations

from virtual_knitting_machine.Knitting_Machine import Knitting_Machine


class Knitout_Line:
    """General class for lines of knitout.

    Attributes:
        comment (str | None): The comment that follows the knitout instruction. None if there is no comment.
        original_line_number (int | None): The line number of this instruction in its original file or None if that is unknown.
        follow_comments(list[Knitout_Comment_Line]): A list of Knitout_Comment_Line objects that follow this line.


    """
    _Lines_Made = 0

    def __init__(self, comment: str | None, interrupts_carriage_pass: bool = False) -> None:
        Knitout_Line._Lines_Made += 1
        self._creation_time: int = Knitout_Line._Lines_Made
        self.comment: str | None = comment
        self.original_line_number: int | None = None
        self.follow_comments: list[Knitout_Comment_Line] = []
        self._interrupts_carriage_pass: bool = interrupts_carriage_pass

    @property
    def interrupts_carriage_pass(self) -> bool:
        """Check if this line interrupts a carriage pass.

        Returns:
            True if this type of line interrupts a carriage pass, False if it
            is only used for comments or setting information.
        """
        return self._interrupts_carriage_pass

    def add_follow_comment(self, comment_line: str) -> None:
        """Add a comment line to comments that follow this line.

        Args:
            comment_line: The comment text to add.
        """
        self.follow_comments.append(Knitout_Comment_Line(comment_line))

    @property
    def has_comment(self) -> bool:
        """Check if this line has a comment.

        Returns:
            True if comment is present.
        """
        return self.comment is not None

    @property
    def comment_str(self) -> str:
        """Get the comment as a formatted string.

        Returns:
            The comment formatted as a string with appropriate formatting.
        """
        if not self.has_comment:
            return "\n"
        else:
            return f";{self.comment}\n"

    def execute(self, machine_state: Knitting_Machine) -> bool:
        """Execute the instruction on the machine state.

        Args:
            machine_state: The knitting machine state to update.

        Returns:
            True if the process completes an update.
        """
        return False

    def __str__(self) -> str:
        return self.comment_str

    @property
    def injected(self) -> bool:
        """Check if instruction was marked as injected.

        Returns:
            True if instruction was marked as injected by a negative line number.
        """
        return self.original_line_number is not None and self.original_line_number < 0

    def id_str(self) -> str:
        """Get string representation with original line number if present.

        Returns:
            String with original line number added if present.
        """
        if self.original_line_number is not None:
            return f"{self.original_line_number}:{self}"[:-1]
        else:
            return str(self)[-1:]

    def __repr__(self) -> str:
        if self.original_line_number is not None:
            return self.id_str()
        else:
            return str(self)

    # def __eq__(self, other):
    #     return str(self) == str(other)

    def __lt__(self, other: Knitout_Line) -> bool:
        if self.original_line_number is None:
            if other.original_line_number is None:
                return False
            else:
                return True
        elif other.original_line_number is None:
            return False
        else:
            return bool(self.original_line_number < other.original_line_number)

    def __hash__(self) -> int:
        return hash(self._creation_time)


class Knitout_Version_Line(Knitout_Line):
    """Represents a knitout version specification line."""

    def __init__(self, version: int = 2, comment: None | str = None):
        """Initialize a version line.

        Args:
            version: The knitout version number. Defaults to 2.
            comment: Optional comment for the version line.
        """
        super().__init__(comment, interrupts_carriage_pass=False)
        self.version: int = version

    def __str__(self) -> str:
        return f";!knitout-{self.version}{self.comment_str}"


class Knitout_Comment_Line(Knitout_Line):
    """Represents a comment line in knitout."""

    def __init__(self, comment: None | str | Knitout_Line):
        """Initialize a comment line.

        Args:
            comment: The comment text, or a Knitout_Line to convert to a comment.
        """
        if isinstance(comment, Knitout_Line):
            if isinstance(comment, Knitout_Comment_Line):
                comment = str(Knitout_Comment_Line.comment_str)
            else:
                comment = f"No-Op:\t{comment}"
        super().__init__(comment, interrupts_carriage_pass=False)

    def execute(self, machine_state: Knitting_Machine) -> bool:
        return True
