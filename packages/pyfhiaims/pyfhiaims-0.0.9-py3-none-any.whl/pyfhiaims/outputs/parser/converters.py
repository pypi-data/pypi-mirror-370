"""Type converters for parsed values."""

import datetime
import re

from pyfhiaims import AimsGeometry


def _to_builtin(pattern, builtin_type):
    """Convert pattern to the builtin type."""

    def _helper(line, _):
        match = re.search(pattern, line, re.DOTALL | re.MULTILINE)
        if match:
            return builtin_type(match.group(1))
        return None

    return _helper


def to_atoms(pattern, from_input=False):
    """Convert aims.out geometry representation to AimsGeometry."""
    from pyfhiaims.geometry.geometry import AimsGeometry

    def _helper(line, _):
        # Capture everything to the next dashed line including it
        match = re.search(
            rf"{pattern}.*\n([\s\S]*?)\n *-{{60,}}", line, re.MULTILINE
        )
        if match is None:
            return None
        lines = match.group()
        # remove fractional coordinates
        lines = lines[: lines.find("Fractional coordinates")]
        lines = lines.split("\n")[2:-1]
        return AimsGeometry.from_strings(lines)
        # with tempfile.TemporaryDirectory() as tmp:
        #     file_name = Path(tmp) / "geometry.in"
        #     with open(file_name, "w") as f:
        #         f.write("\n".join(lines))
        #     atoms = read(file_name, format="aims")

    return _helper

def bsse_to_atoms():
    """Convert BSSE geometry representation to AimsGeometry."""
    def _helper(line, _):
        match = re.search(
            r"-{59,}\n([\s\S]*?)\n *-{59,}", line, re.MULTILINE
        )
        if match is None:
            return None
        lines = match.group().split("\n")[2:-1]
        geom_in = []
        is_empty = False
        for s in lines:
            if "x [A]" in s:
                is_empty = "Ghost" in s
                continue
            bits = s.split()[3:]
            geom_in.append(f"{'empty' if is_empty else 'atom'} "
                           f"{' '.join(bits[1:4])} {bits[0]}")
        return AimsGeometry.from_strings(geom_in)
    return _helper


def to_bool(pattern):
    """Convert pattern to bool."""

    def _helper(line, _):
        return bool(re.search(pattern, line, re.DOTALL | re.MULTILINE))

    return _helper


def to_float(pattern):
    """Convert pattern to float."""
    return _to_builtin(pattern, float)


def to_int(pattern):
    """Convert pattern to int."""
    return _to_builtin(pattern, int)


def to_str(pattern):
    """Convert pattern to date."""
    return _to_builtin(pattern, str)


def to_date(pattern):
    """Convert pattern to date."""
    return _to_builtin(
        pattern, lambda x: datetime.datetime.strptime(x, "%Y%m%d").date()
    )


def to_time(pattern):
    """Convert pattern to a time."""
    return _to_builtin(
        pattern, lambda x: datetime.datetime.strptime(x, "%H%M%S.%f").time()
    )


def to_table(
    pattern,
    *,
    num_rows: int | str,
    header: int = 1,
    dtype: list[type] | tuple[type] | None = None,
):
    """Convert `num_rows` lines after `header` indicated by `pattern` to
    Python 2D list.
    """
    dtype = dtype if dtype is not None else []

    def _helper(line, metadata):
        # we need a local scope variable for not to lose access to num_rows
        n_rows = num_rows if isinstance(num_rows, int) else metadata[num_rows]
        match = re.search(
            rf"{pattern}\n((?:.*\n){{{header+n_rows-1}}})", line, re.MULTILINE
        )
        if match is None:
            return None
        table = match.group(1).split("\n")[header - 1 : -1]
        types = dtype + ([None] * (len(table[0].split()) - len(dtype)))
        result = []
        for table_line in table:
            result.append(
                [
                    t(v)
                    for t, v in zip(types, table_line.split(), strict=False)
                    if t is not None
                ]
            )
        # make it 1D list if only one column is asked for in the parser
        if len(result[0]) == 1:
            result = [r[0] for r in result]
        return result

    return _helper


def to_vector(pattern: str, *, dtype: type = float, multistring: bool = False):
    """Convert a set of numbers to a 1D numpy array.

    Parameters
    ----------
    pattern: str
        A regular expression pattern.
    dtype: type
        A Python type to convert to.
    multistring: bool
        If True, checks for different occurrences of the pattern in a line
        (different matches).

        If False, finds the numbers written in one line
        (different groups within one match).

    """

    def _helper(line, _):
        match = re.findall(pattern, line, re.DOTALL | re.MULTILINE)
        if not match:
            return None
        return (
            [dtype(x) for x in match] if multistring else [dtype(x) for x in match[0]]
        )

    return _helper


def to_matrix(
    pattern: str,
    *,
    dtype: list[type] | tuple[type] | None = None,
):
    """Convert a multi-line string matching a pattern into a 2D matrix.

    Parameters
    ----------
    pattern : str
        A regular expression pattern that captures rows of data as groups.
    dtype : list[type] | tuple[type] | None
        A list or tuple of Python types that specifies the type of each
        column. The length of `dtype` must match the number of groups in
        `pattern`. If None, no conversion is performed.

    Notes
    -----
    - Each match of the `pattern` corresponds to a row in the resulting 2D matrix.
    - The number of data columns in the pattern must match the number of dtypes
    specified.

    """

    def _helper(line, _):
        match = re.findall(pattern, line, re.DOTALL | re.MULTILINE)
        if not match:
            return None
        res = []
        for m in match:
            assert len(m) == len(dtype)
            res.append(
                [
                    dtype_i(m_i)
                    for dtype_i, m_i in zip(dtype, m, strict=False)
                    if dtype_i is not None
                ]
            )
        return res

    return _helper
