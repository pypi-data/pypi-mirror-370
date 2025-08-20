"""Various utilities for pyaims."""


def is_number_string(s: str) -> bool:
    """Check if s is a string made of float numbers and optionally comment sign.

    Parameters
    ----------
    s: str
        A string to check

    Returns
    -------
    bool
        True if the string represents a number

    """
    allowed_chars = set("-.# ")
    return all(char.isdigit() or char in allowed_chars for char in s)
