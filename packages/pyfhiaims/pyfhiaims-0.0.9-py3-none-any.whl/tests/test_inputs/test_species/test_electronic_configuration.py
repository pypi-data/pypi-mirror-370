"""Tests for electronic_configuration module."""

from textwrap import dedent

from pyfhiaims.species_defaults.electronic_configuration import (
    ElectronicConfiguration,
    ElectronicConfigurationType,
)

valence_str = dedent(
    """\
    valence      2  s   2.
    valence      2  p   3."""
)

ionic_str = dedent(
    """\
    ion_occ      6  s   1.
    ion_occ      6  p   1.
    ion_occ      5  d  10.
    ion_occ      4  f  14."""
)


def test_electronic_configuration():
    """Test electronic_configuration"""
    el_config = ElectronicConfiguration.from_strings(valence_str.split("\n"))
    assert el_config.type == ElectronicConfigurationType.VALENCE
    assert el_config.n_electrons == 7
    assert dedent(str(el_config)) == valence_str

    el_config = ElectronicConfiguration.from_strings(ionic_str.split("\n"))
    assert el_config.type == ElectronicConfigurationType.IONIC
    assert el_config.n_electrons == 80
    assert dedent(str(el_config)) == ionic_str
