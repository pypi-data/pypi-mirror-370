"""Parser code for accessing Parglare language support"""
import re

import parglare.exceptions
from importlib_resources import files
from parglare import Grammar, Parser

import knitout_interpreter
from knitout_interpreter.knitout_language.knitout_actions import action
from knitout_interpreter.knitout_operations.Knitout_Line import Knitout_Line


class Knitout_Parser:
    """Parser for reading knitout using the parglare library."""

    def __init__(self, debug_grammar: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> None:
        """Initialize the Knitout parser with optional debugging features.

        Args:
            debug_grammar: Enable grammar debugging. Defaults to False.
            debug_parser: Enable parser debugging. Defaults to False.
            debug_parser_layout: Enable parser layout debugging. Defaults to False.

        Raises:
            FileNotFoundError: If the <knitout.pg> grammar file cannot be located in the package.
        """
        try:
            pg_resource_stream = files(knitout_interpreter.knitout_language).joinpath('knitout.pg')
            self._grammar: Grammar = Grammar.from_file(pg_resource_stream, debug=debug_grammar, ignore_case=True)
        except (FileNotFoundError, AttributeError) as e:
            raise FileNotFoundError(
                f"Could not locate 'knitout.pg' in package 'knitout_interpreter.knitout_language'. "
                f"Please ensure the package is properly installed and the grammar file is included. "
                f"Original error: {e}"
            ) from e
        self._grammar: Grammar = Grammar.from_file(pg_resource_stream, debug=debug_grammar, ignore_case=True)
        self._set_parser(debug_parser, debug_parser_layout)

    def _set_parser(self, debug_parser: bool, debug_parser_layout: bool) -> None:
        """Set up the parser with the current grammar and debugging options.

        Args:
            debug_parser: Enable parser debugging.
            debug_parser_layout: Enable parser layout debugging.
        """
        self._parser: Parser = Parser(self._grammar, debug=debug_parser, debug_layout=debug_parser_layout, actions=action.all)
        self._parser.knitout_parser = self  # make this structure available from actions

    def parse_knitout_to_instructions(self, pattern: str, pattern_is_file: bool = False,
                                      reset_parser: bool = True,
                                      debug_parser: bool = False, debug_parser_layout: bool = False) -> list[Knitout_Line]:
        """Parse knitout pattern into a list of instruction objects.

        Args:
            pattern: Either a file path or the knitout string to be parsed.
            pattern_is_file: If True, treat pattern as a file path. Defaults to False.
            reset_parser: Reset parser to have no prior input. Defaults to True.
            debug_parser: Enable parser debugging. Defaults to False.
            debug_parser_layout: Enable parser layout debugging. Defaults to False.

        Returns:
            List of knitout instructions created by parsing the given pattern.

        Raises:
            parglare.exceptions.ParseError: If there's an error parsing the knitout code.
        """
        codes: list[Knitout_Line] = []
        if reset_parser:
            self._set_parser(debug_parser, debug_parser_layout)
        if pattern_is_file:
            with open(pattern, "r") as pattern_file:
                lines = pattern_file.readlines()
        else:
            lines = pattern.splitlines()
        for i, line in enumerate(lines):
            if not re.match(r'^\s*$', line):
                try:
                    code = self._parser.parse(line)
                except parglare.exceptions.ParseError as e:
                    print(f"Knitout Parsing Error at {i}: {line}")
                    raise e
                if code is None:
                    continue
                else:
                    assert isinstance(code, Knitout_Line), f"Expected Knitout Line but got {code}"
                    codes.append(code)
        return codes


def parse_knitout(pattern: str, pattern_is_file: bool = False, debug_parser: bool = False, debug_parser_layout: bool = False) -> list[Knitout_Line]:
    """Execute the parsing code for the parglare parser.

    This is a convenience function that creates a Knitout_Parser instance
    and parses the given pattern.

    Args:
        pattern: Either a file path or the knitout string to be parsed.
        pattern_is_file: If True, treat pattern as a file path. Defaults to False.
        debug_parser: Enable parser debugging. Defaults to False.
        debug_parser_layout: Enable parser layout debugging. Defaults to False.

    Returns:
        List of knitout instructions created by parsing the given pattern.

    Raises:
        parglare.exceptions.ParseError: If there's an error parsing the knitout code.
        FileNotFoundError: If the grammar file or input file cannot be found.
    """
    parser = Knitout_Parser(debug_parser, debug_parser_layout)
    return parser.parse_knitout_to_instructions(pattern, pattern_is_file, reset_parser=False)
