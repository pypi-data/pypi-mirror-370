"""Tests for basis_function module."""

import pytest

from pyfhiaims.species_defaults.basis_function import (
    BasisFunction,
    BasisFunctionError,
    ConfinedBasisFunction,
    GaussianBasisFunction,
    HydroBasisFunction,
    IonicBasisFunction,
    STOBasisFunction,
)


def test_basis_function():
    """Tests a generic BasisFunction constructor."""
    string = "    hydro 4 f 5.6 # Comment Test"
    basis_function = BasisFunction.from_string(string)
    assert basis_function.type == "hydro"
    assert basis_function.enabled
    assert not basis_function.aux
    assert basis_function.comments[0] == " Comment Test"

    string = "#    hydro 4 f 5.6  # Comment Test"
    basis_function = BasisFunction.from_string(string)
    assert basis_function.type == "hydro"
    assert not basis_function.enabled
    assert not basis_function.aux
    assert basis_function.comments[0] == " Comment Test"

    string = "# for_aux hydro 4 f 5.6"
    basis_function = BasisFunction.from_string(string)
    assert basis_function.type == "hydro"
    assert not basis_function.enabled
    assert basis_function.aux

    with pytest.raises(ValueError, match="No valid basis function type found in"):
        _ = BasisFunction.from_string("asdfg 0 1")


def test_hydro_basis_function():
    """Tests hydrogen-like BasisFunction constructor."""
    string = "    hydro 4 f 5.6 # Comment Test"
    basis_function = HydroBasisFunction.from_string(string)
    assert basis_function.type == "hydro"
    assert basis_function.z_eff == 5.6
    assert basis_function.comments[0] == " Comment Test"


def test_ionic_basis_function():
    """Tests ionic BasisFunction constructor."""
    string = "    ionic 4 d auto # Comment Test"
    basis_function = IonicBasisFunction.from_string(string)
    assert basis_function.n == 4
    assert basis_function.radius == "auto"
    assert basis_function.comments[0] == " Comment Test"
    string = "    ionic 3 d 2.5"
    basis_function = IonicBasisFunction.from_string(string)
    assert basis_function.n == 3
    assert basis_function.radius == 2.5


def test_confined_basis():
    """Test the confined basis function"""
    string = "confined      3  s  0.99"
    basis_function = ConfinedBasisFunction.from_string(string)
    assert basis_function.enabled
    assert basis_function.type == "confined"
    assert basis_function.n == 3
    assert basis_function.l == "s"
    assert basis_function.radius == 0.99
    assert str(basis_function).strip() == string

    string = "# confined 3 s 0.99 # Comment Test"
    basis_function = ConfinedBasisFunction.from_string(string)
    assert not basis_function.enabled


gaussian_str_long = """gaussian    1       7
    315.9000000  0.0039266 # Comment Test
    74.4200000  0.0298811
    23.4800000  0.1272120 # Comment Test
    8.4880000  0.3209430
    3.2170000  0.4554290
    1.2290000  0.2685630
    0.2964000  0.0188336"""


def test_gaussian_basis_function():
    """Tests Gaussian-based BasisFunction constructor."""
    string = "gaussian    0       1  10555500.0000000"
    basis_function = GaussianBasisFunction.from_string(string)
    assert basis_function.enabled
    assert basis_function.type == "gaussian"
    assert basis_function.n == 1
    assert len(basis_function.alpha_i) == 1
    assert not basis_function.aux
    assert basis_function.alpha_i[0] == 1.05555e7
    assert str(basis_function).strip() == string

    string = "# gaussian 0 1  0.105555E+08"
    basis_function = BasisFunction.from_string(string)
    assert not basis_function.enabled

    basis_function = GaussianBasisFunction.from_string(gaussian_str_long)
    print(str(basis_function))
    print(gaussian_str_long)
    assert str(basis_function) == gaussian_str_long

    string = "aux_gaussian 0 1 0.10555E+08"
    basis_function = BasisFunction.from_string(string)
    assert basis_function.aux

    with pytest.raises(BasisFunctionError):
        _ = GaussianBasisFunction(n=2, l=0, alpha_i=[0, 1], coeff_i=None)

    with pytest.raises(BasisFunctionError):
        _ = GaussianBasisFunction(n=2, l=0, alpha_i=[0, 1], coeff_i=[0, 1, 2])

    with pytest.raises(BasisFunctionError):
        _ = GaussianBasisFunction(n=2, l=0, alpha_i=[0, 1, 2], coeff_i=[0, 1])


def test_sto_basis_function():
    """Test the STO basis function"""
    string = "sto      1  0  0.76"
    basis_function = STOBasisFunction.from_string(string)
    assert basis_function.enabled
    assert basis_function.type == "sto"
    assert basis_function.n == 1
    assert basis_function.l == 0
    assert basis_function.zeta == 0.76
    assert str(basis_function).strip() == string

    string = "# sto 1 0   0.76"
    basis_function = STOBasisFunction.from_string(string)
    assert not basis_function.enabled
