"""A class representing BandStructure."""

from dataclasses import dataclass

import numpy as np


@dataclass
class BandStructure:
    """A band structure."""

    is_soc: bool
    is_mulliken: bool
    data: np.ndarray
