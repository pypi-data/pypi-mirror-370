"""Tests for BasisSet class"""

from textwrap import dedent

import pytest

from pyfhiaims.species_defaults.basis_function import HydroBasisFunction
from pyfhiaims.species_defaults.basis_set import BasisSet, TierNotFoundError


def test_basis_set():
    """Test basis sets."""
    basis_string = dedent(
        """\
    #  "First tier" - improvements: -1014.90 meV to -62.69 meV
     hydro 2 s 2.1
     hydro 2 p 3.5
    #  "Second tier" - improvements: -12.89 meV to -1.83 meV
         hydro 1 s 0.85
    #     hydro 2 p 3.7
    #     hydro 2 s 1.2
      for_aux    hydro 3 d 7
    #  "Third tier" - improvements: -0.25 meV to -0.12 meV
     gaussian 0 2
        16.0396781            0.3942297
         6.5038187            0.2499824
    # gaussian 0 2
    #    18.0396781            0.3942297
    #     9.5038187            0.2499824
    #     hydro 4 f 11.2
    #     hydro 3 p 4.8
    #     hydro 4 d 9
    #     hydro 3 s 3.2

    """
    )
    basis_set = BasisSet.from_string(basis_string)
    assert basis_set.n_tiers == 3
    assert len(basis_set.tier(1)) == 2
    assert len(basis_set.tier(2)) == 3
    assert len(basis_set.tier(2, enabled=True)) == 1
    assert len(basis_set.tier(2, enabled=True, aux=True)) == 1
    assert len(basis_set.tier(3, enabled=True)) == 1

    basis_set.activate_tier(2, 1)
    assert len(basis_set.tier(2, enabled=True)) == 2

    basis_set.deactivate_functions(1)
    assert len(basis_set.tier(2, enabled=True)) == 2
    assert len(basis_set.tier(3, enabled=True)) == 0

    basis_set.activate_functions(1)
    assert len(basis_set.tier(2, enabled=True)) == 3

    basis_set.deactivate_tier(2, "all", aux=True)
    assert len(basis_set.tier(2, enabled=True, aux=True)) == 0

    basis_set.activate_tier(3, "all")
    assert len(basis_set.tier(3, enabled=True)) == 6

    basis_set.deactivate_tier(3, 99)
    assert len(basis_set.tier(3, enabled=True)) == 0

    basis_set.deactivate_functions(99)
    assert len(basis_set.tier(1, enabled=True)) == 0

    basis_set.add_function(
        HydroBasisFunction(n=1, l="s", z_eff=2.4), tier=3, active=True, aux=False
    )
    basis_set.add_function(
        HydroBasisFunction(n=1, l="s", z_eff=1.4), active=True, aux=False
    )
    assert len(basis_set.tier(3, enabled=True)) == 1
    assert len(basis_set.tier(6, enabled=True)) == 1

    with pytest.raises(TierNotFoundError):
        _ = basis_set.tier(100)

    with pytest.raises(TierNotFoundError):
        _ = basis_set.activate_tier(100)

    with pytest.raises(TierNotFoundError):
        _ = basis_set.add_function(
            HydroBasisFunction(n=1, l="s", z_eff=1.4), tier=100, active=True, aux=False
        )
