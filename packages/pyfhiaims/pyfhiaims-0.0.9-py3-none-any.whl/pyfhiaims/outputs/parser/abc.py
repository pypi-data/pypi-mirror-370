"""A main output file parser for FHI-aims.

Realizes the Deterministic State Machine pattern.
"""

from __future__ import annotations

import importlib
import inspect
import random
import re
import string
from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import IO, Any, ClassVar

from monty.io import zopen

from .converters import to_str
from .utils import update

INT = r"[-\d]+"
FLOAT = r"[-+.\d]+"
EXP = r"[-+.E\d]+"


def parser_classes(module) -> dict[str, type[ChunkParser]]:
    """Return the dict of all the file and chunk parser classes declared in
    the current module.
    """
    result = {}
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if issubclass(cls, ChunkParser):
            result[cls.name] = cls
    return result


def _get_parser(parser_class, header_line):
    """Inject the header line into the ChunkParser instance."""

    def _factory(file_descriptor: str | Path | IO, parent: Parser = None) -> Parser:
        return parser_class(file_descriptor, parent, header_line)

    return _factory


class Parser:
    """Abstract parser class for FHI-aims output files."""

    name: str = ""

    def __init__(
        self, file_descriptor: str | Path | IO, parent: FileParser = None
    ) -> None:
        """Construct a base class for the parser.

        Parameters
        ----------
        file_descriptor: str | Path | IO
            A name or handle of the main output file
        parent: Parser
            A parent parser for the current instance

        """
        # get the module in which the actual implementation is located
        # (parsers.py) and available parsers within that module
        module = importlib.import_module(self.__module__)
        self._available_parsers = parser_classes(module)
        self.result = {}
        self.warnings = []
        self.errors = []
        # propagate metadata along inheritance line
        self.parent = parent
        if self.parent is None:
            self.run_metadata = {}
        else:
            self.run_metadata = self.parent.run_metadata
        self.next = None
        # open the file to parse
        if isinstance(file_descriptor, str | Path):
            self.fd = zopen(file_descriptor, "rt")
            self.is_root = True
        else:
            self.fd = file_descriptor
            self.is_root = False

    def add_parsed_values(self, parser_name: str, **kwargs):
        """Update the specified parser's values with the provided key-value pairs.
        Only parsers available in the system can be updated. Each value should either
        be of type string or returned from a function from a `converters` module.
        Raises an error if the parser is not available or if a value is of an
        unsupported type.

        Args:
            parser_name: The name of the parser to be updated.
            kwargs: Key-value pairs to be added to the parser's values.

        Raises:
            ValueError: If the parser is not available
            TypeError: If any of the provided values are not of a valid type.

        """
        parser = self._available_parsers.get(parser_name, None)
        if parser is None:
            raise ValueError(f"Parser {parser_name} is not available.")
        for v in kwargs.values():
            if not isinstance(v, str | Callable):
                raise TypeError(
                    f"The parsed value {v} should either be a string or returned from "
                    f"`converters.to_...` function. Got {type(v)} instead.`."
                )
        parser.values.update(kwargs)

    def __del__(self):
        """Close the file if it is the root parser."""
        if self.is_root:
            self.fd.close()

    @abstractmethod
    def parse(self):
        """Parse the output file by dividing it into chunks.

        It then parses each chunk separately.

        Returns
        -------
        dict: a parsed dictionary

        """
        raise NotImplementedError

    @abstractmethod
    def annotate(self, annotated_file: str | Path | IO):
        """Annotates the output file by adding the chunk name and ID to each line.

        Parameters
        ----------
        annotated_file: str | Path | IO
            The name of the file to write annotations to.
            If None, write the annotated file to stdout.

        """
        raise NotImplementedError


class FileParser(Parser):
    """The main output file parser."""

    initial_chunk: str

    def __init__(
        self,
        file_descriptor: str | Path | IO,
        parent: Parser = None,
        header_line: str | None = None,
    ) -> None:
        """Construct the main Parser object.

        Parameters
        ----------
        file_descriptor : str | Path | IO
            A name or handle of the main output file
        parent: Parser
            The parent parser
        header_line: str | None
            The first line to serach for

        """
        super().__init__(file_descriptor, parent)
        # inject header line into the ChunkParser class
        self._initial_chunk = _get_parser(
            self._available_parsers[self.initial_chunk], header_line
        )

    def parse(self) -> dict:
        """Parse the output file by dividing it into chunks.

        It then parses each chunk separately.

        Returns
        -------
        dict: a parsed dictionary

        """
        self.fd.seek(0)
        # instantiate ChunkParser with header line already injected
        current_chunk = self._initial_chunk(self.fd, parent=self)
        # can we create the `parse_results` structure preliminary?
        parse_results = {}
        while current_chunk:
            chunk_results = current_chunk.parse()
            if chunk_results or current_chunk.parsed_key:
                update(parse_results, chunk_results, current_chunk.parsed_key)
            if current_chunk.next is None:
                break
            current_chunk = current_chunk.next(self.fd, parent=self)
        self.result = parse_results
        return self.result

    def annotate(self, annotated_file: str | Path | IO | None = None) -> None:
        """Annotates the output file by adding the chunk name and ID to each line.

        Parameters
        ----------
        annotated_file: str | Path | IO
            The name of the file to write annotations to.
            If None, write the annotated file to stdout.

        """
        self.fd.seek(0)
        if isinstance(annotated_file, str | Path):
            annotated_fd = open(annotated_file, "w")  # noqa: SIM115
        else:
            annotated_fd = annotated_file
        current_chunk = self._initial_chunk(self.fd, parent=self)
        while current_chunk:
            current_chunk.annotate(annotated_fd)
            if current_chunk.next is None:
                break
            current_chunk = current_chunk.next(self.fd, parent=self)
        if isinstance(annotated_fd, IO):
            annotated_fd.close()


class ChunkParser(Parser):
    """An abstract class for the output file chunks.

    Attributes
    ----------
    name : str
        the name of the chunk parser
    title_line : str
        The start line of the given chunk in the output file
    values : dict[str, Any]
        the dict of the names and regular expressions for the values that
        may be found in the chunk
    next_chunks : list[str | dict]
        the collection of lines and runtime choices that define the next chunk
    parsed_key: str
        the key under which the values are stored in the parse results

    Parameters
    ----------
    file_descriptor : str | Path | IO
        a path to the file or an open output file descriptor

    """

    title_line: str = ""
    parsed_key: str = ""
    values: ClassVar[dict[str, Any]] = {}
    metadata: ClassVar[dict[str, Any]] = {}
    next_chunks: ClassVar[list[str | dict[str, Any]]] = []

    def __init__(
        self,
        file_descriptor: str | Path | IO,
        parent: Parser = None,
        header_line: str | None = None,
    ) -> None:
        """Concstruct the parser.

        Parameters
        ----------
        file_descriptor: str | Path | IO
            The output file
        parent: Parser
            The parent parser
        header_line: str | None
            The first line to serach for

        """
        super().__init__(file_descriptor, parent)
        self.header_line = header_line
        self.uuid = "".join(random.choices(string.ascii_letters + string.digits, k=4))
        self._next_parsers = self._get_next_parsers()

    def _get_next_parsers(self) -> list[dict[str, Any]]:
        """Return the list of dictionaries containing the available next parsers
        and corresponding title lines.
        """
        next_parsers = []
        for chunk_meta in self.next_chunks:
            if isinstance(chunk_meta, str):
                next_parsers.append(
                    {
                        "parser": self._available_parsers[chunk_meta],
                        "line": self._available_parsers[chunk_meta].title_line,
                    }
                )
            elif isinstance(chunk_meta, dict) and "runtime_choices" in chunk_meta:
                parser_choices = chunk_meta.get("runtime_choices", {})
                on_parser = True
                for choice, value in parser_choices.items():
                    # boolean: check only for the existence of the key
                    if (
                        isinstance(value, bool)
                        and ((choice in self.run_metadata) != value)
                    ) or (
                        not isinstance(value, bool)
                        and self.run_metadata.get(choice, None) != value
                    ):
                        on_parser = False
                if on_parser:
                    next_parsers.append(
                        {
                            "parser": self._available_parsers[chunk_meta["chunk"]],
                            "line": self._available_parsers[
                                chunk_meta["chunk"]
                            ].title_line,
                        }
                    )
        return next_parsers

    def _check_for_next(self, line):
        """Decides on the chunk which a given line of the output should
        belong to.

        Parameters
        ----------
        line : str
            a line of the output file

        Returns
        -------
            None if the line belongs to this chunk; a FileChunk class if it belongs
            to another chunk

        """
        # find the next parser by comparing the line with the given regex
        for parser_meta in self._next_parsers:
            line_regex = parser_meta["line"]
            if re.search(line_regex, line):
                return _get_parser(parser_meta.get("parser", None), header_line=line)
        return None

    def collect(self):
        """Collect all lines belonging to this chunk."""
        lines = [self.header_line] if self.header_line is not None else []
        while line := self.fd.readline():
            next_chunk = self._check_for_next(line)
            if next_chunk is not None:
                self.next = next_chunk
                break
            lines.append(line)

        # TODO: Here check if the output file is actually complete!
        return "".join(lines)

    def parse(self) -> dict:
        """Parse the output file chunk genericlly."""
        line = self.collect()
        parse_result = {}
        # 1. values parsing
        for k, v in self.values.items():
            if not inspect.isfunction(v):
                v = to_str(v)
            # bring metadata to converter function; useful for parser variables
            match = v(line, self.run_metadata)
            if match is not None:
                parse_result[k] = match  # the first parenthesized subgroup
        # 2. metadata parsing
        for k, v in self.metadata.items():
            if not inspect.isfunction(v):
                v = to_str(v)
            match = v(line, self.run_metadata)
            if match is not None:
                self.parent.run_metadata[k] = match  # the first parenthesized subgroup
        # 3. warnings and errors parsing (ones that begin with optional
        # space and asterisk)
        self.parent.errors += re.findall(r"^(?: ?\*.*\n)+[\s\n]*\Z", line, re.MULTILINE)
        self.parent.warnings += re.findall(r"^(?: ?\*.*\n)+", line, re.MULTILINE)
        self.result = parse_result
        return self.result

    def annotate(self, annotated_file: IO) -> None:
        """Annotates the given chunk."""
        line = self.collect()
        # metadata parsing
        for k, v in self.metadata.items():
            if not inspect.isfunction(v):
                v = to_str(v)
            match = v(line, self.run_metadata)
            if match is not None:
                self.parent.run_metadata[k] = match  # the first parenthesized subgroup
        # get annotation and annotate
        truncated_name = self.name if len(self.name) < 15 else self.name[:12] + "..."
        annotation = f"{truncated_name:>15s}:{self.uuid}"
        annotated_lines = [f"{annotation} -> {el}" for el in line.split("\n")]
        if isinstance(annotated_file, IO):
            annotated_file.write("\n".join(annotated_lines))
        else:
            print("\n".join(annotated_lines), end="")
