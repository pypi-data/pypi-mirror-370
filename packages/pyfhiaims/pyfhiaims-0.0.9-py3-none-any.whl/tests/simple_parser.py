"""A simple parser written to test the outputs.parser approach."""

from pyfhiaims.outputs.parser import converters
from pyfhiaims.outputs.parser.abc import EXP, FLOAT, INT, ChunkParser, FileParser


class SimpleParser(FileParser):
    """A simple parser written to test the outputs.parser approach."""
    name = "root"
    initial_chunk = "a"


class AParser(ChunkParser):
    name = "a"
    values = {
        "version": r"Version: (\S*)"
    }
    metadata = {}
    next_chunks = ["b", "c"]
    parsed_key = ""


class BParser(ChunkParser):
    name = "b"
    title_line = "B CHUNK"
    values = {
        "b1": converters.to_int(fr" \| B1 = ({INT})"),
        "b2": converters.to_float(fr" \| B2 = {FLOAT} Ry ({FLOAT}) eV"),
        "b3": converters.to_float(fr"B3 = ({EXP})"),
        "b4": converters.to_float(fr" \| B4 = ({INT})")
    }
    next_chunks = ["c"]
    parsed_key = "b_values"


class CParser(ChunkParser):
    name = "c"
    title_line = "--- C "
    values = {
        "t": converters.to_float(fr"time = ({FLOAT})"),
        "all_good": converters.to_bool(r"Everything is good"),
    }
    metadata = {}
    next_chunks = ["c", "d"]
    parsed_key = "b_values.c_values[]"


class DParser(ChunkParser):
    name = "d"
    title_line = "Converged"
    values = {
        "end_time": converters.to_time(rf"End time: ({FLOAT})")
    }
    metadata = {}
    parsed_key = "b_values.c_values"
