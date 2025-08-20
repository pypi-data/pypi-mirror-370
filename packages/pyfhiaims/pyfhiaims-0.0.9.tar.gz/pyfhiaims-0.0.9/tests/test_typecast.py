"""Tests for `utils.typecast` submodule."""

import numpy as np

from pyfhiaims.utils.typecast import to_matrix3d, to_vector3d


def test_typecast():
    """Tests utils.typecast submodule."""
    a = (3, 2, 3)
    vec = to_vector3d(a)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (3,)
    assert vec.dtype == float
    b = [[True, False, True], [False, True, False], [True, True, False]]
    mat = to_matrix3d(b, dtype=bool)
    assert isinstance(mat, np.ndarray)
    assert mat.shape == (3, 3)
    assert mat.dtype == bool
