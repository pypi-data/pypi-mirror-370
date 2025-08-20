"""Utilities for the FHI-aims parser."""

import collections.abc


class NamedDict(dict):
    """A named dict to access items as attributes."""

    __getattr__ = dict.__getitem__


def update(d: dict, u: dict, key: str) -> dict:
    """Update a dictionary `d` with the dictionary `u` under the `key`.

    Parameters
    ----------
    d: dict
        A dictionary to update
    u: dict
        An update dictionary
    key: str
        A key to the update dictionary

    """
    if not key:
        d.update(u)
        return d
    steps = key.split(".")
    step = steps[0]
    # the square brackets only present in the last step of the key
    if step.endswith("[]"):
        # append a list
        d[step[:-2]] = [*d.get(step[:-2], []), u]
    else:
        d_step = d.get(step, {})
        if isinstance(d_step, collections.abc.Mapping):
            d[step] = update(d_step, u, ".".join(steps[1:]))
        else:
            # d_step has to be a list; we update a last dict in it
            assert isinstance(d_step, collections.abc.Iterable)
            d[step][-1] = update(d_step[-1], u, ".".join(steps[1:]))
    return d
