"""Tests for AimsControl object."""

import numpy as np
import pytest

from pyfhiaims.control import AimsControl
from pyfhiaims.control.cube import AimsCube
from pyfhiaims.errors import PyaimsError
from pyfhiaims.geometry import AimsGeometry

control_in_content = """#
# List of parameters used to initialize the calculator:
#     output_level:MD_light
#     xc:pw-lda
#     relativistic:atomic_zora scalar
#     relax_geometry:trm 1E-2
#     relax_unit_cell:full
#     k_grid:2 2 2
#     output:[]
#===============================================================================
output_level                                      MD_light
xc                                                pw-lda
relativistic                                      atomic_zora scalar
relax_geometry                                    trm 1E-2
relax_unit_cell                                   full
k_grid                                            2 2 2
#===============================================================================


##################################################################################
#
# Read in species defaults for Al atom from pyfhiaims
#
##################################################################################
  species               Al
#     global species definitions
  nucleus               13.0
  mass                  26.9815386
#
  l_hartree             4
#
  cut_pot               3.5 1.5 1.0
  basis_dep_cutoff      0.0001
#
  radial_base    41   5.0000
  radial_multiplier        1
  angular_grids  specified
  division       0.6594  110
  division       0.8170  194
  division       0.9059  302
  outer_grid     302
##################################################################################
#
#  Definition of "minimal" basis
#
##################################################################################
#     valence basis states
    valence      3  s   2.
    valence      3  p   1.
#     ion occupancy
    ion_occ      3  s   1.
    ion_occ      2  p   6.
##################################################################################
#
#  Suggested additional basis functions. For production calculations,
#  uncomment them one after another (the most important basis functions are
#  listed first).
#
#  These were set using pyfhiaims, original may files have additional comments
#
##################################################################################
#  First tier
             ionic      3  d  auto
             ionic      3  p  auto
#            hydro      4  f  4.7
             ionic      3  s  auto
#  Second tier
#            hydro      5  g  7.0
#            hydro      3  d  6.0
#            hydro      2  s  11.6
#            hydro      2  p  0.9
#  Third tier
#            hydro      5  f  7.6
#            hydro      4  p  7.2
#            hydro      4  s  3.7
#            hydro      4  d  7.6
#  Fourth tier
#            hydro      4  d  13.6
#            hydro      5  g  11.2
#            hydro      4  d  0.9
#            hydro      1  s  0.4
#            hydro      4  p  0.1
#            hydro      5  f  9.8
#  Further basis functions
#            hydro      4  p  5.0
##################################################################################
#
# Read in species defaults for S atom from pyfhiaims
#
##################################################################################
  species               S
#     global species definitions
  nucleus               16.0
  mass                  32.065
#
  l_hartree             4
#
  cut_pot               3.5 1.5 1.0
  basis_dep_cutoff      0.0001
#
  radial_base    44   5.0000
  radial_multiplier        1
  angular_grids  specified
  division       0.4665  110
  division       0.5810  194
  division       0.7139  302
  outer_grid     302
##################################################################################
#
#  Definition of "minimal" basis
#
##################################################################################
#     valence basis states
    valence      3  s   2.
    valence      3  p   4.
#     ion occupancy
    ion_occ      3  s   1.
    ion_occ      3  p   3.
##################################################################################
#
#  Suggested additional basis functions. For production calculations,
#  uncomment them one after another (the most important basis functions are
#  listed first).
#
#  These were set using pyfhiaims, original may files have additional comments
#
##################################################################################
#  First tier
             ionic      3  d  auto
             hydro      2  p  1.8
#            hydro      4  f  7.0
             ionic      3  s  auto
#  Second tier
#            hydro      4  d  6.2
#            hydro      5  g  10.8
#            hydro      4  p  4.9
#            hydro      5  f  10.0
#            hydro      1  s  0.8
#  Third tier
#            hydro      3  d  3.9
#            hydro      3  d  2.7
#            hydro      5  g  12.0
#            hydro      4  p  10.4
#            hydro      5  f  12.4
#            hydro      2  s  1.9
#  Fourth tier
#            hydro      4  d  10.4
#            hydro      4  p  7.2
#            hydro      4  d  10.0
#            hydro      5  g  19.2
#            hydro      4  s  12.0
##################################################################################
#
# Read in species defaults for Zn atom from pyfhiaims
#
##################################################################################
  species               Zn
#     global species definitions
  nucleus               30.0
  mass                  65.409
#
  l_hartree             4
#
  cut_pot               3.5 1.5 1.0
  basis_dep_cutoff      0.0001
#
  radial_base    53   5.0000
  radial_multiplier        1
  angular_grids  specified
  division       0.5114   50
  division       0.8989  110
  division       1.2692  194
  division       1.6226  302
  outer_grid     302
##################################################################################
#
#  Definition of "minimal" basis
#
##################################################################################
#     valence basis states
    valence      4  s   2.
    valence      3  p   6.
    valence      3  d  10.
#     ion occupancy
    ion_occ      4  s   1.
    ion_occ      3  p   6.
    ion_occ      3  d   9.
##################################################################################
#
#  Suggested additional basis functions. For production calculations,
#  uncomment them one after another (the most important basis functions are
#  listed first).
#
#  These were set using pyfhiaims, original may files have additional comments
#
##################################################################################
#  First tier
             hydro      2  p  1.7
             hydro      3  s  2.9
             hydro      4  p  5.4
             hydro      4  f  7.8
             hydro      3  d  4.5
#  Second tier
#            hydro      5  g  10.8
#            hydro      2  p  2.4
#            hydro      3  s  6.2
#            hydro      3  d  3.0
#  Third tier
#            hydro      6  h  15.2
#            ionic      4  p  auto
#            hydro      5  s  12.8
#            hydro      4  f  5.4
#            hydro      4  d  7.0
#            hydro      4  f  20.0
#            hydro      3  p  2.2
#            hydro      5  f  6.4
#            hydro      5  g  8.0"""


def test_control(data_dir, tmp_path):
    control_dir = data_dir / "control"
    control_in = AimsControl.from_file(control_dir / "al2zns4.in")

    geometry_dir = data_dir / "geometry"
    geometry = AimsGeometry.from_file(geometry_dir / "scr.in")
    for key, val in control_in.species_defaults.items():
        geometry.set_species(key, val)

    content = control_in.get_content(
        geometry=geometry, verbose_header=True
    )

    assert control_in_content == content

    assert control_in["output_level"] == "MD_light"

    assert control_in["xc"] == "pw-lda"
    control_in["xc"] = "LDA"
    assert control_in["xc"] == "LDA"
    assert control_in.parameters["xc"] == "LDA"

    assert "Al" in control_in.species_defaults

    control_in["output"] = "test"
    assert control_in["output"] == []

    control_in.outputs.append("test")
    assert control_in["output"] == ["test"]

    del control_in["output"]
    assert control_in["output"] == []

    control_in.outputs.append("mulliken")
    control_in["cubes"] = [
        AimsCube(
            type="total_density",
            origin=[0.1, 0.2, -0.3],
            edges=np.eye(3) * 0.2,
        )
    ]
    control_in.write_file(
        geometry=geometry, writer=tmp_path, verbose_header=False, overwrite=True
    )

    new_control_in = AimsControl.from_dict(control_in.as_dict())
    for key, val in control_in.parameters.items():
        assert new_control_in[key] == val

    new_control_in["smearing"] = ("fermi-dirac", 0.1)
    assert (
        "occupation_type                                   fermi 0.1"
        in new_control_in.get_content(geometry)
    )

    new_control_in["smearing"] = ("methfessel-paxton", 0.1, 1)
    assert (
        "occupation_type                                   methfessel-paxton 0.100000 1"
        in new_control_in.get_content(geometry)
    )

    new_control_in["vdw_correction_hirshfeld"] = True
    new_control_in["relax_geometry"] = ("trm", 1e-4)
    new_control_in["charge"] = 1.0
    new_control_in["compute_forces"] = True
    new_control_in["compute_stress"] = None
    # new_control_in["species_dir"] = "./"

    assert "vdw_correction_hirshfeld" in new_control_in.get_content(
        geometry
    )
    assert (
        "relax_geometry                                    trm 0.0001"
        in new_control_in.get_content(geometry)
    )
    assert (
        "charge                                            1"
        in new_control_in.get_content(geometry)
    )
    assert (
        "compute_forces                                    .true."
        in new_control_in.get_content(geometry)
    )
    assert "compute_stress" not in new_control_in.get_content(geometry)

    new_control_in["xc"] = "libxc LDA_X+LDA_C_PW"
    assert "override_warning_libxc" in new_control_in.get_content(geometry)

    new_control_in["occupation_type"] = ("gaussian", 0.1)
    with pytest.raises(
        ValueError,
        match="Both smearing and occupation_type can"
    ):
        _ = new_control_in.get_content(geometry)

    with pytest.raises(
        ValueError,
        match="control.in file already in"
    ):
        control_in.write_file(
            geometry=geometry, writer=tmp_path, verbose_header=False, overwrite=False
        )

    del control_in["k_grid"]
    with pytest.raises(
        ValueError,
        match="k-grid must be defined for periodic"
    ):
        control_in.write_file(
            geometry=geometry, writer=tmp_path, verbose_header=False, overwrite=True
        )

    with pytest.raises(
        PyaimsError,
        match="Reading control.in from file does not work with cubes yet"
    ):
        _ = AimsControl.from_file(f"{tmp_path}/control.in")

    with pytest.raises(KeyError):
        _ = control_in["afeasfas"]
    # print(control_in.species_defaults["Co"].content)
