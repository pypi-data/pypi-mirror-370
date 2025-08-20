"""Test the AimsCube interface"""

import numpy as np
import pytest

from pyfhiaims.geometry.atom import FHIAimsAtom

content_base = """atom         0.000000000000e+00   1.100000000000e+00  -2.500000000000e-01 H
    velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00
    initial_charge 0.200000000000
    initial_moment 0.500000000000
    constrain_relaxation x
    constraint_region 1
    magnetic_moment 0.200000000000
    nuclear_spin 0.300000000000
    isotope 3
    RT_TDDFT_initial_velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00"""  # noqa: E501

content_frac = """atom_frac    0.000000000000e+00   1.100000000000e+00  -2.500000000000e-01 H
    velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00
    initial_charge 0.200000000000
    initial_moment 0.500000000000
    constrain_relaxation x
    constraint_region 1
    magnetic_moment 0.200000000000
    nuclear_spin 0.300000000000
    isotope 3
    RT_TDDFT_initial_velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00"""  # noqa: E501

content_frac_wrap = """atom_frac    0.000000000000e+00   1.000000000000e-01   7.500000000000e-01 H
    velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00
    initial_charge 0.200000000000
    initial_moment 0.500000000000
    constrain_relaxation x
    constraint_region 1
    magnetic_moment 0.200000000000
    nuclear_spin 0.300000000000
    isotope 3
    RT_TDDFT_initial_velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00"""  # noqa: E501

content_empty = """empty        0.000000000000e+00   1.100000000000e+00  -2.500000000000e-01 H
    velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00
    initial_charge 0.200000000000
    initial_moment 0.500000000000
    constrain_relaxation x
    constraint_region 1
    magnetic_moment 0.200000000000
    nuclear_spin 0.300000000000
    isotope 3
    RT_TDDFT_initial_velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00"""  # noqa: E501

content_psuedocore = """pseudocore   0.000000000000e+00   1.100000000000e+00  -2.500000000000e-01 H
    velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00
    initial_charge 0.200000000000
    initial_moment 0.500000000000
    constrain_relaxation x
    constraint_region 1
    magnetic_moment 0.200000000000
    nuclear_spin 0.300000000000
    isotope 3
    RT_TDDFT_initial_velocity   1.000000000000e+00   2.000000000000e+00   3.000000000000e+00"""  # noqa: E501


def test_atom(tmp_path):
    """Test the AimsCube Interface"""
    atom = FHIAimsAtom(
        symbol="H",
        position=[0.0, 1.1, -0.25],
        velocity=[1, 2, 3],
        initial_charge=0.2,
        initial_moment=0.5,
        constraints=(True, False, False),
        constraint_region=1,
        magnetic_response=False,
        magnetic_moment=0.2,
        nuclear_spin=0.3,
        isotope=3,
        is_empty=False,
        is_pseudocore=False,
        RT_TDDFT_initial_velocity=[1, 2, 3],
    )

    assert atom.to_string() == content_base

    atom.set_fractional(np.eye(3))
    assert atom.to_string() == content_frac

    atom.set_fractional(np.eye(3), wrap=True)
    assert atom.to_string() == content_frac_wrap

    atom.is_empty = True
    assert atom.to_string() == content_empty

    atom.is_empty = False
    atom.is_pseudocore = True
    assert atom.to_string() == content_psuedocore

    with pytest.raises(KeyError):
        _ = FHIAimsAtom(symbol="Asdf", position=[0, 0, 0])
