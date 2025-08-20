"""Type casting utils from pymatgen that are useful."""

from collections.abc import Sequence
from typing import Annotated, Literal, TypeVar

import numpy as np
import numpy.typing as npt

_T = TypeVar("_T", bound=np.generic)

Vector3D = Annotated[npt.NDArray[_T], Literal[3]]
Matrix3D = Annotated[npt.NDArray[_T], Literal[3]]


def to_vector3d(sequence: Sequence, dtype=float) -> Vector3D:
    """Type casting to 3D vector of floats."""
    if len(sequence) != 3:
        raise ValueError("Vector3D requires a length of 3")
    return np.array(sequence, dtype=dtype)


def to_matrix3d(sequence: Sequence, dtype=float) -> Matrix3D:
    """Type casting to 3D matrix of floats."""
    if (len(sequence) != 3) and all(len(row) != 3 for row in sequence):
        raise ValueError("Matrix3D requires a length of 3 in both dimsensions.")

    return np.array(sequence, dtype=dtype)
