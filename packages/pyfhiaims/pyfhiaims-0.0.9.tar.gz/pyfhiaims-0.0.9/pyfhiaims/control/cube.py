"""Classes for reading/manipulating/writing FHI-aims cube files.

Works for aims cube objects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from monty.json import MontyDecoder, MSONable

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Self

    from pymatgen.util.typing import Tuple3Floats, Tuple3Ints

__author__ = "Thomas A. R. Purcell"
__version__ = "1.0"
__email__ = "purcellt@arizona.edu"
__date__ = "July 2024"

ALLOWED_AIMS_CUBE_TYPES = (
    "delta_density",
    "spin_density",
    "stm",
    "total_density",
    "total_density_integrable",
    "long_range_potential",
    "hartree_potential",
    "xc_potential",
    "delta_v",
    "ion_dens",
    "dielec_func",
    "elf",
)

ALLOWED_AIMS_CUBE_TYPES_STATE = (
    "first_order_density",
    "eigenstate",
    "eigenstate_imag",
    "eigenstate_density",
)

ALLOWED_AIMS_CUBE_FORMATS = (
    "cube",
    "gOpenMol",
    "xsf",
)


@dataclass
class AimsCube(MSONable):
    """The FHI-aims cubes.

    Attributes:
        type (str): The value to be outputted as a cube file
        origin (Sequence[float] or tuple[float, float, float]): The origin of the cube
        edges (Sequence[Sequence[float]]): Specifies the edges of a cube: dx, dy, dz
            dx (float): The length of the step in the x direction
            dy (float): The length of the step in the y direction
            dx (float): The length of the step in the x direction
        points (Sequence[int] or tuple[int, int, int]): The number of points
            along each edge
        spin_state (int): The spin-channel to use either 1 or 2
        kpoint (int): The k-point to use (the index of the list printed from
            `output k_point_list`)
        filename (str): The filename to use
        format (str): The format to output the cube file in: cube, gOpenMol, or xsf
        elf_type (int): The type of electron localization function to use (
            see FHI-aims manual)

    """

    type: str = field(default_factory=str)
    origin: Sequence[float] | Tuple3Floats = field(
        default_factory=lambda: [0.0, 0.0, 0.0]
    )
    edges: Sequence[Sequence[float]] = field(default_factory=lambda: 0.1 * np.eye(3))
    points: Sequence[int] | Tuple3Ints = field(default_factory=lambda: [0, 0, 0])
    format: str = "cube"
    spin_state: int | None = None
    kpoint: int | None = None
    filename: str | None = None
    elf_type: int | None = None

    def __eq__(self, other: object) -> bool:
        """Check if two cubes are equal to each other."""
        if not isinstance(other, AimsCube):
            return NotImplemented

        if self.type != other.type:
            return False

        if not np.allclose(self.origin, other.origin):
            return False

        if not np.allclose(self.edges, other.edges):
            return False

        if not np.allclose(self.points, other.points):
            return False

        if self.format != other.format:
            return False

        if self.spin_state != other.spin_state:
            return False

        if self.kpoint != other.kpoint:
            return False

        if self.filename != other.filename:
            return False

        return self.elf_type == other.elf_type

    def __hash__(self):
        """Return the hash of the AimsCube object."""
        return hash(self.to_json())

    def __post_init__(self) -> None:
        """Check the inputted variables to make sure they are correct.

        Raises:
            ValueError: If any of the inputs is invalid

        """
        split_type = self.type.split()
        cube_type = split_type[0]
        if split_type[0] in ALLOWED_AIMS_CUBE_TYPES:
            if len(split_type) > 1:
                raise ValueError(
                    f"{cube_type=} can not have a state associated with it"
                )
        elif split_type[0] in ALLOWED_AIMS_CUBE_TYPES_STATE:
            if len(split_type) != 2:
                raise ValueError(f"{cube_type=} must have a state associated with it")
        else:
            raise ValueError("Cube type undefined")

        if self.format not in ALLOWED_AIMS_CUBE_FORMATS:
            raise ValueError(
                f"{self.format} is invalid. Cube files must have a format of "
                f"{ALLOWED_AIMS_CUBE_FORMATS}"
            )

        valid_spins = (1, 2, None)
        if self.spin_state not in valid_spins:
            raise ValueError(f"Spin state must be one of {valid_spins}")

        if len(self.origin) != 3:
            raise ValueError("The cube origin must have 3 components")

        if len(self.points) != 3:
            raise ValueError("The number of points per edge must have 3 components")

        if len(self.edges) != 3:
            raise ValueError("Only three cube edges can be passed")

        for edge in self.edges:
            if len(edge) != 3:
                raise ValueError("Each cube edge must have 3 components")

        if self.elf_type is not None and self.type != "elf":
            raise ValueError(
                "elf_type is only used when the cube type is elf. "
                "Otherwise it must be None"
            )

    @property
    def control_block(self) -> str:
        """The block of text for the control.in file of the Cube."""
        cb = f"output cube {self.type}\n"
        cb += (
            f"    cube origin {self.origin[0]: .12e} {self.origin[1]: .12e} "
            f"{self.origin[2]: .12e}\n"
        )
        for idx in range(3):
            cb += f"    cube edge {self.points[idx]} "
            cb += f"{self.edges[idx][0]: .12e} "
            cb += f"{self.edges[idx][1]: .12e} "
            cb += f"{self.edges[idx][2]: .12e}\n"
        cb += f"    cube format {self.format}\n"
        if self.spin_state is not None:
            cb += f"    cube spinstate {self.spin_state}\n"
        if self.kpoint is not None:
            cb += f"    cube kpoint {self.kpoint}\n"
        if self.filename is not None:
            cb += f"    cube filename {self.filename}\n"
        if self.elf_type is not None:
            cb += f"    cube elf_type {self.elf_type}\n"

        return cb

    def as_dict(self) -> dict[str, Any]:
        """Get a dictionary representation of the geometry.in file."""
        dct: dict[str, Any] = {}
        dct["@module"] = type(self).__module__
        dct["@class"] = type(self).__name__
        dct["type"] = self.type
        dct["origin"] = self.origin
        dct["edges"] = self.edges
        dct["points"] = self.points
        dct["format"] = self.format
        dct["spin_state"] = self.spin_state
        dct["kpoint"] = self.kpoint
        dct["filename"] = self.filename
        dct["elf_type"] = self.elf_type
        return dct

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> Self:
        """Initialize from dictionary.

        Args:
            dct (dict[str, Any]): The MontyEncoded dictionary

        Returns:
            AimsCube

        """
        attrs = (
            "type",
            "origin",
            "edges",
            "points",
            "format",
            "spin_state",
            "kpoint",
            "filename",
            "elf_type",
        )
        decoded = {key: MontyDecoder().process_decoded(dct[key]) for key in attrs}

        return cls(**decoded)
