"""Define the atom object for FHI-aims geometry files."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

import numpy as np

from .periodic_table import ATOMIC_SYMBOLS_TO_NUMBERS

if TYPE_CHECKING:
    from pyfhiaims.utils.typecast import Matrix3D, Vector3D


class FHIAimsAtomType(Enum):
    """Enum type for atoms."""

    ATOM = 1
    EMPTY = 2
    PSEUDOCORE = 3


@dataclass
class FHIAimsAtom:
    """Atom object for FHI-aims.

    Parameters
    ----------
    symbol: Sequence[str]
        List of symbols for each nucleus in the structure
    number: Optional[Sequence[int]]
        Atomic number for the nuclei
    position: Sequence[Vector3D]
        The position of each nucleus in space
    fractional_position: Optional[Sequence[Vector3D]]
        The fractional_position of the atoms
    velocity: Optional[Sequence[Vector3D]]
        The velocity of each nucleus in space
    initial_charge: Sequence[float]
        The initial charge for each nuclei
    initial_moment: Sequence[float]
        The initial magnetic moment for each nuclei
    constraints: Sequence[tuple[bool, bool, bool]]
        Fix_atom constraints for each nucleus and direction
    is_empty: Optional[Sequence[bool]]
        Specifies if site is for an empty_site
    constraint_region: Optional[Sequence[int | None]]
        Assigns the immediately preceding atom to the region labelled number.
        number is the integer number of a spatial region, which must correspond to a
        region defined by keyword constraint_electrons in file control.in
    is_pseudocore: Optional[Sequence[bool]]
        True if site is a pseudocore
    magnetic_response: Optional[Sequence[bool]]
        Includes the current atom in the magnetic response calculations. If only
        the magnetizability is required, this keyword need not be used in geometry.in.
        Otherwise, the calculation of the shieldings or J-couplings is aborted if no
        atoms are flagged for MR calculations in geometry.in
    magnetic_moment: Optional[Sequence[float]]
        Overrides the default magnetic moment for the given atom. The default values
        (in units of the nuclear magneton µN ) can be found in
        MagneticResponse/MR_nuclear_data.f90. In case of J-couplings, the isotopes
        used are also printed in the output.
    nuclear_spin: Optional[Sequence[float]]
        Overrides the default nuclear spin for the given atom. The default
        values can be found in MagneticResponse/MR_nuclear_data.f90 and are also
        printed in the output for J-coupling calculations.
    isotope: Optional[Sequence[int]]
        Overrides the default isotope mass number for the given atom. For
        more flexibility, the magnetic moment and spin can be specified separately
        with the above keywords. The default isotopes numbers can be found in
        MagneticResponse/MR_nuclear_data.f90.
    RT_TDDFT_initial_velocity: Sequence[Vector3D]
        Initial velocity of corresponding (i.e. last specified) atom when
        peforming RT-TDDFT-Ehrenfest dynamics

    """

    symbol: str = None
    number: int | None = None
    position: Vector3D = None
    fractional_position: Vector3D | None = None
    velocity: Vector3D | None = None
    initial_charge: float = 0.0
    initial_moment: float = 0.0
    constraints: tuple[bool, bool, bool] | None = None
    constraint_region: int | None = None
    magnetic_response: bool | None = None
    magnetic_moment: float | None = None
    nuclear_spin: float | None = None
    isotope: int | None = None
    is_empty: bool = None
    is_pseudocore: bool = None
    RT_TDDFT_initial_velocity: Vector3D | None = None

    def __post_init__(self):
        symbol = re.search(r"[A-Za-z]+", self.symbol).group(0)
        self.number = ATOMIC_SYMBOLS_TO_NUMBERS[symbol]

    def set_fractional(self, lattice_vectors: Matrix3D, wrap: bool = False):
        """Set the fractional postion given lattice vectors.

        Parameters
        ----------
        lattice_vectors: Matrix3D
            The lattice vectors for ths system
        wrap: bool
            True it to wrap atoms into the unit cell

        """
        self.fractional_position = np.linalg.solve(
            lattice_vectors.T, np.transpose(self.position)
        ).T
        if wrap:
            self.fractional_position %= 1.0
            self.fractional_position %= 1.0

    def to_string(self):
        """Convert an FHIAimsAtom object to geometry.in string."""
        pos = self.position
        # what happens if both empty and pseudocore are chosen?
        if self.is_empty:
            atom_str = "empty     "
        elif self.is_pseudocore:
            atom_str = "pseudocore"
        elif self.fractional_position is not None:
            atom_str = "atom_frac "
            pos = self.fractional_position
        else:
            atom_str = "atom      "

        content_str = [
            f"{atom_str} "
            + " ".join([f"{pi:>20.12e}" for pi in pos])
            + f" {self.symbol}"
        ]

        if self.velocity is not None:
            content_str.append(
                "    velocity " + " ".join([f"{vel:>20.12e}" for vel in self.velocity])
            )

        if np.abs(self.initial_charge) > 1e-12:
            content_str.append(f"    initial_charge {self.initial_charge:.12f}")

        if self.initial_moment > 1e-12:
            content_str.append(f"    initial_moment {self.initial_moment:.12f}")

        if self.constraints is not None and np.any(self.constraints):
            content_str.append(
                str(
                    f"    constrain_relaxation "
                    f"{'x ' if self.constraints[0] else ''}"
                    f"{'y ' if self.constraints[1] else ''}"
                    f"{'z' if self.constraints[2] else ''}"
                ).rstrip()
            )

        if self.constraint_region is not None and self.constraint_region > 0:
            content_str.append(f"    constraint_region {self.constraint_region}")

        if self.magnetic_response is not None and self.magnetic_response:
            content_str.append("    magnetic_response")
        if self.magnetic_moment is not None and np.abs(self.magnetic_moment) > 1e-12:
            content_str.append(f"    magnetic_moment {self.magnetic_moment:.12f}")
        if self.nuclear_spin is not None and np.abs(self.nuclear_spin) > 1e-12:
            content_str.append(f"    nuclear_spin {self.nuclear_spin:.12f}")
        if self.isotope is not None and self.isotope > 0:
            content_str.append(f"    isotope {self.isotope}")
        if self.RT_TDDFT_initial_velocity is not None:
            content_str.append(
                "    RT_TDDFT_initial_velocity "
                + " ".join([f"{vel:>20.12e}" for vel in self.RT_TDDFT_initial_velocity])
            )

        return "\n".join(content_str)
