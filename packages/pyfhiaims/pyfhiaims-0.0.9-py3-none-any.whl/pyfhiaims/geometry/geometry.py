"""The geometry representation for geometry.in files."""

from __future__ import annotations

import time
import warnings
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, TextIO

import numpy as np

from pyfhiaims.geometry.atom import ATOMIC_SYMBOLS_TO_NUMBERS, FHIAimsAtom
from pyfhiaims.species_defaults.species import SpeciesDefaults
from pyfhiaims.utils.typecast import Matrix3D, Vector3D, to_matrix3d


class InvalidGeometryError(Exception):
    """Exception raised if there is a problem with the input geometry."""

    def __init__(self, message: str) -> None:
        """Initialize the error with the message, message."""
        self.message = message
        super().__init__(self.message)


@dataclass
class AimsGeometry:
    """Geometry for the structure to run the calculation for.

    Parameters
    ----------
    atoms: Sequence[FHIAimsAtom]
        The Atoms for the geometry
    lattice_vectors: Optional[Matrix3D]
        The initial set of lattice vectors for the structure
    lattice_constraints: Sequence[tuple[bool, bool, bool]]
        fix lattice constraints for each nucleus and direction
    species_dict: dict[str, SpeciesDefaults]
        Dictionary to get the species for each symbol in the structure
    hessian_block: Optional[Sequence[tuple[int, int, Matrix3D]]]
        In geometry.in, allows to specify a Hessian matrix explicitly, with one
        line for each 3×3 block.
        The option block consists of nine numbers in column-first
        (Fortran) order. The 3×3 block corresponding to j_atom, i_atom is initialized
        by the transposed of block. The Hessian matrix is input in units of eV/Å2.
    hessian_block_lv: Optional[Sequence[tuple[float, float, Matrix3D]]]
        hessian_block for lattice vectors
    hessian_block_lv_atoms: Optional[Sequence[tuple[float, float, Matrix3D]]]
        hessian_block for degrees of freedom between lattice vectors and atoms
    hessian_file: Optional[bool]
        Indicates that there exists a hessian.aims file to be used to construct
        the Hessian.
    trust_radius: Optional[float]
        allows to specify the initial trust radius value for the trm
        relaxation algorithm
    symmetry_n_params: Optional[tuple[int, int]]
        Number of parameters for the lattice and fractional degrees of freedom
    symmetry_params: Optional[Sequence[str]]
        The list of all parametric constraints parameters
    symmetry_lv: Optional[tuple[str, str, str]]
        The list of parametric constraints for the lattice_vectors
    symmetry_frac: Optional[Sequence[tuple[str, str, str]]]
        The list of parametric constraints for the fractional coordinates
    symmetry_frac_change_threshold: Optional[float]
        Specifies the maximum allowed change in the initial structure to any
        fractional coordinate after applying the parametric constraints. If set to 1.0,
        then these tests will be ignored. max_change is the maximum allowed change in
        the fractional coordinates of an atom
    homogeneous_field: Optional[Vector3D]
        Allows performing a calculation for a system in a homogeneous electrical
        field E in units of V/AA.
    multipole: Optional[Sequence[tuple[float, float, float, int, float]]]
        Places the center of an electrostatic multipole field at a specified location,
        to simulate an embedding potential.
            x : x coordinate of the multipole.
            y : y coordinate of the multipole.
            z : z coordinate of the multipole.
            order : Integer number, which specifies the order of the multipole
                    (0 or 1 ≡ monopole or dipole).
            charge : Real number, specifies the charge associated with the multipole.
    esp_constraint: Optional[tuple[float, float, float] | tuple[float, float]]
        PBC only. Define the constraints for the fit of the ESP-charges for
        each atom. Depending on the chosen method (`esp_constraint` method in
        control.in). Method 1 needs three parameters (χ, J00, w) 3.167 and method 2
        needs two parameters (q0, β) 3.169 as defined above
    verbatim_writeout: Optional[bool]
        If True write the geometry.in file into the output file
    calculate_friction: Optional[bool]
        Calculate friction for this geometry

    """

    atoms: Sequence[FHIAimsAtom] = None
    lattice_vectors: Matrix3D[float] | None = None
    lattice_constraints: Vector3D[bool] | None = None
    species_dict: dict[str, SpeciesDefaults] | None = field(default_factory=dict)
    hessian_block: Sequence[tuple[int, int, Matrix3D]] | None = None
    hessian_block_lv: Sequence[tuple[float, float, Matrix3D]] | None = None
    hessian_block_lv_atoms: Sequence[tuple[float, float, Matrix3D]] | None = None
    hessian_file: bool | None = None
    trust_radius: float | None = None
    symmetry_n_params: tuple[int, int, int] | None = None
    symmetry_params: Sequence[str] | None = None
    symmetry_lv: tuple[str, str, str] | None = None
    symmetry_frac: Sequence[tuple[str, str, str]] | None = None
    symmetry_frac_change_threshold: float | None = None
    homogeneous_field: Vector3D | None = None
    multipole: Sequence[tuple[float, float, float, int, float]] | None = None
    esp_constraint: tuple[float, float, float] | tuple[float, float] | None = None
    verbatim_writeout: bool | None = None
    calculate_friction: bool | None = None

    def __post_init__(self):
        """Set up optional inputs given information/verify all inputs are correct."""
        if self.lattice_vectors is not None:
            self.lattice_vectors = np.array(self.lattice_vectors)
            if self.lattice_vectors.shape != (3, 3):
                raise InvalidGeometryError(
                    "Lattice vectors must be None or a 3x3 matrix"
                )

            if np.abs(np.linalg.det(self.lattice_vectors)) < 1e-12:
                raise InvalidGeometryError(
                    "Lattice vectors must be linearly independent"
                )

            if self.lattice_constraints is None:
                self.lattice_constraints = np.zeros((3, 3), dtype=bool)
        else:
            if self.lattice_constraints is not None:
                raise InvalidGeometryError(
                    "Lattice vectors must be defined for "
                    "lattice_constraints to be defined."
                )

            if any(
                inp is not None
                for inp in [
                    self.symmetry_n_params,
                    self.symmetry_params,
                    self.symmetry_lv,
                    self.symmetry_frac,
                    self.symmetry_frac_change_threshold,
                ]
            ):
                raise InvalidGeometryError(
                    "Lattice vectors must be defined when "
                    "using parametric constraints."
                )
        self.verify_object_lens()

    @classmethod
    def _get_property_names(cls, atomic=False):
        """Return a list of all properties defined for this geometry."""
        if atomic:
            return [
                k
                for k, v in cls.__dict__.items()
                if isinstance(v, property) and k not in ["ase_atoms", "structure"]
            ]
        # noinspection PyTypeChecker
        return [f.name for f in fields(cls)]

    def __repr__(self):
        """Return a representation of the geometry, featuring a simple chemical
        formula.
        """
        symbols = Counter(a.symbol for a in self.atoms)
        return (
            f"{self.__class__.__name__}"
            f"({''.join(f'{k}{v}' for k, v in symbols.items())})"
        )

    def __len__(self):
        """Get the length of the geometry."""
        return len(self.symbols)

    def verify_object_lens(self):
        """Verify the sizes of each input."""
        for item in ["lattice_constraints", "symmetry_lv"]:
            val = getattr(self, item, None)
            if val is not None and np.array(val).shape != (3, 3):
                raise InvalidGeometryError(
                    f"The shape of {item} must be 3x3 not {np.array(val).shape}"
                )

    @classmethod
    def from_file(cls, in_file: Path | str | TextIO) -> AimsGeometry:
        """Read in a geometry.in file and construct a Geometry object.

        Parameters
        ----------
        in_file: str | Path | TextIO
            File to load in

        Returns
        -------
        AimsGeometry
            The Geometry associated with the file

        """
        if isinstance(in_file, str | Path):
            with open(in_file) as fd:
                lines = fd.readlines()
        else:
            lines = in_file.readlines()

        return cls.from_strings(lines)

    @classmethod
    def from_strings(cls, lines: list[str]) -> AimsGeometry:
        """Read in a geometry.in file and construct a Geometry object.

        Parameters
        ----------
        lines: list[str]
            a list of all lines in the file.

        Returns
        -------
            The Geometry object associated with the file

        """
        lattice_vectors = []
        symbols: list[str] = []
        coords: list[Vector3D] = []

        is_empty: list[bool] = []
        is_pseudocore: list[bool] = []
        is_fractional: list[bool] = []

        hessian_block: None | list[tuple[int, int, Matrix3D]] = []
        hessian_block_lv: None | list[tuple[float, float, Matrix3D]] = []
        hessian_block_lv_atoms: None | list[tuple[float, float, Matrix3D]] = []

        symmetry_n_params: None | tuple[int, int, int] = (0, 0, 0)
        symmetry_params: None | Sequence[str] = []
        symmetry_lv: None | list[list[str]] = []
        symmetry_frac: None | list[list[str]] = []

        multipole: None | list[tuple[float, float, float, int, float]] = []

        symmetry_frac_change_threshold: None | float = None
        hessian_file: None | bool = None
        trust_radius: None | float = None
        homogeneous_field: Vector3D = None
        esp_constraint: None | tuple[float, ...] = None
        verbatim_writeout: None | bool = None
        calculate_friction: None | bool = None

        velocities: dict[int, Vector3D] = {}
        initial_charge: dict[int, float] = {}
        initial_moment: dict[int, float] = {}
        nuclear_constraints: dict[int, list[bool]] = {}
        lattice_constraints: None | dict[int, list[bool]] = {}
        constraint_regions: dict[int, int | None] = {}
        magnetic_response: dict[int, bool] = {}
        magnetic_moment: dict[int, float] = {}
        nuclear_spin: dict[int, float] = {}
        isotope: dict[int, float] = {}
        RT_TDDFT_initial_velocity: dict[int, Vector3D] = {}

        last_add: str = ""
        for line in lines:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            inp = line.split("#")[0].split()

            if inp[0] in ["atom", "atom_frac", "empty", "pseudocore"]:
                symbols.append(inp[4])
                coords.append([float(ii) for ii in inp[1:4]])
                is_fractional.append(inp[0] == "atom_frac")
                is_empty.append(inp[0] == "empty")
                is_pseudocore.append(inp[0] == "pseudocore")
                last_add = "atom"
            elif inp[0] == "lattice_vector":
                lattice_vectors.append([float(ii) for ii in inp[1:4]])
                last_add = "lattice"
            elif inp[0] == "initial_moment":
                initial_moment[len(coords) - 1] = float(inp[1])
            elif inp[0] == "initial_charge":
                initial_charge[len(coords) - 1] = float(inp[1])
            elif inp[0] == "constrain_relaxation":
                if last_add == "atom":
                    nuclear_constraints[len(coords) - 1] = _create_constraints(inp)
                if last_add == "lattice":
                    lattice_constraints[len(coords) - 1] = _create_constraints(inp)
            elif inp[0] == "velocity":
                velocities[len(coords) - 1] = [float(ii) for ii in inp[1:4]]
            elif inp[0] == "RT_TDDFT_initial_velocity":
                RT_TDDFT_initial_velocity[len(coords) - 1] = [
                    float(ii) for ii in inp[1:4]
                ]
            elif inp[0] == "constraint_region":
                constraint_regions[len(coords) - 1] = int(inp[1])
            elif inp[0] == "magnetic_response":
                magnetic_response[len(coords) - 1] = True
            elif inp[0] == "magnetic_moment":
                magnetic_moment[len(coords) - 1] = float(inp[1])
            elif inp[0] == "nuclear_spin":
                nuclear_spin[len(coords) - 1] = float(inp[1])
            elif inp[0] == "isotope":
                isotope[len(coords) - 1] = float(inp[1])
            elif inp[0] == "symmetry_frac_change_threshold":
                symmetry_frac_change_threshold = float(inp[1])
            elif inp[0] == "hessian_file":
                hessian_file = True
            elif inp[0] == "trust_radius":
                trust_radius = float(inp[1])
            elif inp[0] == "homogeneous_field":
                homogeneous_field = np.array([float(e) for e in inp[1:]])
            elif inp[0] == "multipole":
                multipole.append(
                    (
                        float(inp[1]),
                        float(inp[2]),
                        float(inp[3]),
                        int(inp[4]),
                        float(inp[5]),
                    )
                )
            elif inp[0] == "esp_constraint":
                esp_constraint = tuple([float(ii) for ii in inp[1:]])
            elif inp[0] == "verbatim_writeout":
                verbatim_writeout = ".true." in inp[1]
            elif inp[0] == "calculate_friction":
                calculate_friction = ".true." in inp[1]
            elif inp[0] == "hessian_block":
                hessian_block.append(
                    (
                        int(inp[1]),
                        int(inp[2]),
                        np.array([float(ii) for ii in inp[3:12]]).reshape((3, 3)),
                    )
                )
            elif inp[0] == "hessian_block_lv":
                hessian_block_lv.append(
                    (
                        int(inp[1]),
                        int(inp[2]),
                        np.array([float(ii) for ii in inp[3:12]]).reshape((3, 3)),
                    )
                )
            elif inp[0] == "hessian_block_lv_atoms":
                hessian_block_lv_atoms.append(
                    (
                        int(inp[1]),
                        int(inp[2]),
                        np.array([float(ii) for ii in inp[3:12]]).reshape((3, 3)),
                    )
                )
            elif inp[0] == "symmetry_n_params":
                symmetry_n_params = (int(inp[1]), int(inp[2]), int(inp[3]))
            elif inp[0] == "symmetry_params":
                symmetry_params = inp[1:]
            elif inp[0] == "symmetry_lv":
                symmetry_lv.append([ii.strip() for ii in line[11:].strip().split(",")])
            elif inp[0] == "symmetry_frac":
                symmetry_frac.append(
                    [ii.strip() for ii in line[13:].strip().split(",")]
                )

        def dct2arr(
            dct: dict[int, Any], n_comp: int
        ) -> np.ndarray[Any, np.dtype[bool]] | None:
            """Convert a dictionary of atom indexes and values to an array."""
            if len(dct) == 0:
                return None
            values = list(dct.values())
            if isinstance(values[0], Sequence | np.ndarray):
                to_ret = np.zeros((n_comp, len(values[0])), dtype=type(values[0][0]))
            else:
                to_ret = np.zeros(n_comp, dtype=type(values[0]))
            for key, val in dct.items():
                to_ret[key] = val
            return to_ret

        if len(lattice_vectors) > 0:
            try:
                lattice_vectors = to_matrix3d(lattice_vectors)
            except AssertionError:
                raise InvalidGeometryError("There must be 3 lattice vectors")

            lattice_constraints = dct2arr(lattice_constraints, 3)

        for cc, coord in enumerate(coords):
            if is_fractional[cc]:
                coords[cc] = list(np.dot(coord, lattice_vectors))

        atoms = []
        for aa, sym in enumerate(symbols):
            atoms.append(
                FHIAimsAtom(
                    symbol=sym,
                    position=coords[aa],
                    velocity=velocities.get(aa),
                    initial_charge=initial_charge.get(aa, 0.0),
                    initial_moment=initial_moment.get(aa, 0.0),
                    constraints=nuclear_constraints.get(aa),
                    constraint_region=constraint_regions.get(aa),
                    magnetic_response=magnetic_response.get(aa),
                    magnetic_moment=magnetic_moment.get(aa),
                    nuclear_spin=nuclear_spin.get(aa),
                    isotope=isotope.get(aa),
                    is_empty=is_empty[aa],
                    is_pseudocore=is_pseudocore[aa],
                    RT_TDDFT_initial_velocity=RT_TDDFT_initial_velocity.get(aa),
                )
            )

        if len(lattice_vectors) > 0:
            for aa in range(len(atoms)):
                atoms[aa].set_fractional(lattice_vectors)

        if symmetry_n_params == (0, 0, 0):
            symmetry_lv = None
            symmetry_frac = None
            symmetry_params = None
            symmetry_n_params = None
            symmetry_frac_change_threshold = None

        if len(lattice_vectors) == 0:
            lattice_vectors = None
            lattice_constraints = None

        if len(hessian_block) == 0:
            hessian_block = None
        if len(hessian_block_lv) == 0:
            hessian_block_lv = None
        if len(hessian_block_lv_atoms) == 0:
            hessian_block_lv_atoms = None
        if len(multipole) == 0:
            multipole = None

        return cls(
            atoms=atoms,
            lattice_vectors=lattice_vectors,
            lattice_constraints=lattice_constraints,
            hessian_block=hessian_block,
            hessian_block_lv=hessian_block_lv,
            hessian_block_lv_atoms=hessian_block_lv_atoms,
            hessian_file=hessian_file,
            trust_radius=trust_radius,
            symmetry_n_params=symmetry_n_params,
            symmetry_params=symmetry_params,
            symmetry_lv=symmetry_lv,
            symmetry_frac=symmetry_frac,
            symmetry_frac_change_threshold=symmetry_frac_change_threshold,
            homogeneous_field=homogeneous_field,
            multipole=multipole,
            esp_constraint=esp_constraint,
            verbatim_writeout=verbatim_writeout,
            calculate_friction=calculate_friction,
        )

    @classmethod
    def from_atoms(
        cls,
        atoms,
        remove_velocities: bool = False,
        geo_constrain: bool = False,
        make_empty: list[int] | None = None,
        scaled: bool = False,
        wrap: bool = False,
    ) -> AimsGeometry:
        """Create an AimsGeometry from an ase.Atoms object.

        Parameters
        ----------
        atoms: ase.Atoms
            The atoms object to convert
        remove_velocities:bool
            If True don't add velocities to the geometry
        geo_constrain: bool
            If true add parameteric constraints
        make_empty: list[int]
            A list of indexes, to make an atom empty
        scaled: bool
            If True setup fractional coordinates
        wrap: bool
            If True and scaled is True wrap atoms into the unit cell

        """
        try:
            from ase.atoms import Atoms
            from ase.constraints import (
                FixAtoms,
                FixCartesian,
                FixCartesianParametricRelations,
                FixScaledParametricRelations,
            )
        except ModuleNotFoundError:
            raise TypeError("ase modules not found")

        if not isinstance(atoms, Atoms):
            raise TypeError(
                f"The atoms objectis not of type ase.Atoms, but f{type(atoms)}"
            )

        if scaled and not np.all(atoms.pbc):
            raise ValueError(
                "Requesting scaled for a calculation where scaled=True, but "
                "the system is not periodic"
            )

        if geo_constrain:
            if not scaled and np.all(atoms.pbc):
                warnings.warn(
                    "Setting scaled to True because a symmetry_block is detected.",
                    stacklevel=2,
                )
                scaled = True
            elif not np.all(atoms.pbc):
                warnings.warn(
                    "Parameteric constraints can only be used in periodic systems.",
                    stacklevel=2,
                )
                geo_constrain = False

        if (make_empty is not None) and (np.max(make_empty) >= len(atoms)):
                raise ValueError(
                    "The max value of make_empty (len(ghosts)) must not "
                    f"exceed the number of atoms {len(atoms)}"
                )

        geometry_props = {
            k: v
            for k, v in atoms.info.items()
            if k in AimsGeometry._get_property_names()
        }

        atomic_props = {
            k: v
            for k, v in atoms.info.items()
            if k in AimsGeometry._get_property_names(atomic=True)
        }

        symmetry_params = [[], []]
        symmetry_n_params = None
        symmetry_lv = None
        symmetry_frac = None
        cart_const = {}
        for const in atoms.constraints:
            if geo_constrain and isinstance(const, FixScaledParametricRelations):
                symmetry_params[1] = const.params
                symmetry_frac = const.expressions
            elif geo_constrain and isinstance(const, FixCartesianParametricRelations):
                symmetry_params[0] = const.params
                symmetry_lv = const.expressions
            elif isinstance(const, FixAtoms):
                cart_const.update(
                    dict.fromkeys(const.get_indices(), (True, True, True))
                )
            elif isinstance(const, FixCartesian):
                for ind in const.index:
                    cart_const[ind] = tuple(mm for mm in const.mask)

        if not remove_velocities:
            atomic_props["velocities"] = [
                v if any(v) else None for v in atoms.get_velocities()
            ]

        aims_atoms = []
        for i_at, atom in enumerate(atoms):
            atom_props = {singular(k): v[i_at] for k, v in atomic_props.items()}
            const = atom_props.pop("nuclear_constraint", None)
            aims_atoms.append(
                FHIAimsAtom(
                    symbol=atom.symbol,
                    position=atom.position,
                    initial_charge=atom.charge,
                    initial_moment=atom.magmom,
                    constraints=cart_const.get(i_at),
                    **atom_props,
                )
            )

        wrap = wrap and not geo_constrain
        if scaled:
            for atom in aims_atoms:
                atom.set_fractional(atoms.cell.array, wrap)

        if make_empty is not None:
            for aa in make_empty:
                aims_atoms[aa].is_empty = True

        if symmetry_lv is not None or symmetry_frac is not None:
            if symmetry_lv is None or symmetry_frac is None:
                raise ValueError("Both symmetry_lv and symmetry_frac must be defined")
            symmetry_n_params = (
                len(symmetry_params[0]),
                len(symmetry_params[1]),
                len(symmetry_params[0]) + len(symmetry_params[1]),
            )
            symmetry_params = symmetry_params[0] + symmetry_params[1]
        else:
            symmetry_params = None

        return cls(
            atoms=aims_atoms,
            lattice_vectors=None if atoms.cell.rank < 3 else atoms.cell,
            symmetry_n_params=symmetry_n_params,
            symmetry_params=symmetry_params,
            symmetry_lv=symmetry_lv,
            symmetry_frac=symmetry_frac,
            **geometry_props,
        )

    @classmethod
    def from_structure(cls, structure) -> AimsGeometry:
        """Create an AimsGeometry from an ase.Atoms object.

        Parameters
        ----------
        structure: Structure | Molecule
            The atoms object to convert

        """
        try:
            from pymatgen.core import Molecule, Species, Structure
        except ModuleNotFoundError:
            raise TypeError("pymatgen modules not found")

        if not isinstance(structure, Structure) and not isinstance(structure, Molecule):
            raise TypeError(
                f"The structure object is not a Structure or Molecule, "
                f"but type {type(structure)}"
            )

        lattice_vectors = getattr(structure, "lattice", None)
        if lattice_vectors is not None:
            lattice_vectors = lattice_vectors.matrix

        atoms = []
        for site in structure:
            element = site.species_string.split(",spin=")[0]
            charge = site.properties.get("charge", None)
            spin = site.properties.get("magmom", None)
            coord = site.coords
            v = site.properties.get("velocity", None)

            if isinstance(site.specie, Species) and site.specie.spin is not None:
                if spin is not None and spin != site.specie.spin:
                    raise ValueError(
                        "species.spin and magnetic moments don't agree. "
                        "Please only define one"
                    )
                spin = site.specie.spin
            elif spin is None:
                spin = 0.0

            if isinstance(site.specie, Species) and site.specie.oxi_state is not None:
                if charge is not None and charge != site.specie.oxi_state:
                    raise ValueError(
                        "species.oxi_state and charge don't agree. "
                        "Please only define one"
                    )
                charge = site.specie.oxi_state
            elif charge is None:
                charge = 0.0

            atoms.append(
                FHIAimsAtom(
                    symbol=element,
                    position=coord,
                    velocity=v,
                    initial_charge=charge,
                    initial_moment=spin,
                )
            )

        return cls(atoms=atoms, lattice_vectors=lattice_vectors)

    def load_species(self, species_directory: str | Path, overwrite: bool = False):
        """Create a species dictionary for the atoms.

        Parameters
        ----------
        species_directory:str | Path
            The Path to load the species into
        overwrite: bool
            True then overwrite existing species defaults

        """
        for sym in np.unique([at.symbol for at in self.atoms]):
            if sym in self.species_dict and not overwrite:
                warnings.warn(f"Won't overwrite species for {sym}", stacklevel=1)

            number = ATOMIC_SYMBOLS_TO_NUMBERS[sym]
            if number < 100:
                self.species_dict[sym] = SpeciesDefaults.from_file(
                    f"{species_directory}/{number:02d}_{sym}_default"
                )
            else:
                self.species_dict[sym] = SpeciesDefaults.from_file(
                    f"{species_directory}/{number:03d}_{sym}_default"
                )

    def set_species(self, sym: str, species: SpeciesDefaults):
        """Set a species default for a given symbol.

        Parameters
        ----------
        sym: str
            The symbol to add the species for
        species: SpeciesDefaults
            The species for the symbol

        """
        self.species_dict[sym] = species

    def get_species(self, sym: str) -> SpeciesDefaults:
        """Get a species default for a given symbol.

        Parameters
        ----------
        sym: str
            The symbol to add the species for

        Returns
        -------
            The species for the symbol

        """
        return self.species_dict[sym]

    def to_string(self):
        """Get the file content for this geometry."""
        content_str = []
        if self.lattice_vectors is not None and len(self.lattice_vectors) == 3:
            for lv, lv_const in zip(
                self.lattice_vectors, self.lattice_constraints, strict=False
            ):
                content_str.append(
                    f"lattice_vector {lv[0]:.15e} {lv[1]:.15e} {lv[2]:.15e}"
                )
                if np.any(lv_const):
                    content_str.append(
                        f"    constrain_relaxation "
                        f"{'x ' if lv_const[0] else ''}"
                        f"{'y ' if lv_const[1] else ''}"
                        f"{'z' if lv_const[2] else ''}"
                    )
        for atom in self.atoms:
            content_str.append(atom.to_string())

        if self.homogeneous_field is not None:
            if len(self.homogeneous_field) != 3:
                raise InvalidGeometryError(
                    "The provided homogeneous_field value is invalid"
                )
            content_str.append(
                f"homogeneous_field {self.homogeneous_field[0]:>20.12e} "
                f"{self.homogeneous_field[1]:>20.12e} "
                f"{self.homogeneous_field[2]:>20.12e}"
            )

        if self.multipole is not None:
            for mm, multipole in enumerate(self.multipole):
                if len(multipole) != 5:
                    raise InvalidGeometryError(
                        f"The provided {mm}th multipole value is invalid"
                    )
                content_str.append(
                    f"multipole {multipole[0]:>20.12e} {multipole[1]:>20.12e} "
                    f"{multipole[2]:>20.12e} {multipole[3]} "
                    f"{multipole[4]:>20.12e}"
                )
            # TODO: Specify a dipole moment to multipoles

        if self.esp_constraint is not None:
            if len(self.esp_constraint) not in (2, 3):
                raise InvalidGeometryError(
                    "The provided esp_constraint value is invalid"
                )
            content_str.append(
                f"esp_constraint "
                f"{' '.join(f'{x:>20.12e}' for x in self.esp_constraint)}"
            )

        if self.verbatim_writeout is not None:
            content_str.append(
                f"verbatim_writeout "
                f"{'.true.' if self.verbatim_writeout else '.false.'}"
            )

        if self.calculate_friction is not None:
            content_str.append(
                f"calculate_friction "
                f"{'.true.' if self.calculate_friction else '.false.'}"
            )

        if self.symmetry_n_params:
            content_str.append(
                f"symmetry_n_params "
                f"{self.symmetry_n_params[0]} {self.symmetry_n_params[1]} "
                f"{self.symmetry_n_params[2]}"
            )

        if self.symmetry_params:
            content_str.append("symmetry_params " + " ".join(self.symmetry_params))
        if self.symmetry_lv is not None:
            for line in self.symmetry_lv:
                content_str.append("symmetry_lv " + " , ".join(line))
        if self.symmetry_frac is not None:
            for line in self.symmetry_frac:
                content_str.append("symmetry_frac " + " , ".join(line))
        if self.symmetry_frac_change_threshold:
            content_str.append(
                f"symmetry_frac_change_threshold {self.symmetry_frac_change_threshold}"
            )

        if self.hessian_block is not None:
            for line in self.hessian_block:
                content_str.append(
                    f"hessian_block {line[0]} {line[1]} "
                    + " ".join([f"{ll:>20.12e}" for ll in np.array(line[2]).flatten()])
                )
        if self.hessian_block_lv is not None:
            for line in self.hessian_block_lv:
                content_str.append(
                    f"hessian_block_lv {line[0]} {line[1]} "
                    + " ".join([f"{ll:>20.12e}" for ll in np.array(line[2]).flatten()])
                )
        if self.hessian_block_lv_atoms is not None:
            for line in self.hessian_block_lv_atoms:
                content_str.append(
                    f"hessian_block_lv_atoms {line[0]} {line[1]} "
                    + " ".join([f"{ll:>20.12e}" for ll in np.array(line[2]).flatten()])
                )

        if self.hessian_file:
            content_str.append("hessian_file")
        if self.trust_radius is not None:
            content_str.append(f"trust_radius {self.trust_radius}")
        return "\n".join(content_str)

    def write_file(self, filename: str | Path | TextIO, header=None) -> None:
        """Write the geometry file."""
        if header is None:
            header = "\n".join(
                [
                    "#" + "=" * 79,
                    "# File written by pyfhiaims",
                    f"# {time.asctime()}",
                    "#" + "=" * 79,
                    "",
                ]
            )

        if isinstance(filename, str | Path):
            with open(filename, "w") as fd:
                content = header + self.to_string()
                fd.write(content)
        else:
            filename.write(header + self.to_string())

    @property
    def symbols(self):
        """The atomic symbol for each atom."""
        return [at.symbol for at in self.atoms]

    @property
    def numbers(self):
        """The atomic number for each atom."""
        return [at.number for at in self.atoms]

    @property
    def positions(self):
        """The position of each atom."""
        return [at.position for at in self.atoms]

    @property
    def fractional_positions(self):
        """The fractional positions of each atom."""
        return [at.fractional_position for at in self.atoms]

    @property
    def velocities(self):
        """The velocity for each atom."""
        return [at.velocity for at in self.atoms]

    @property
    def RT_TDDFT_initial_velocities(self):
        """The real-time TDDFT velocity for each atom."""
        return [at.RT_TDDFT_initial_velocity for at in self.atoms]

    @property
    def initial_charges(self):
        """The initial charge for each atom."""
        return [at.initial_charge for at in self.atoms]

    @property
    def initial_moments(self):
        """The initial moment for each atom."""
        return [at.initial_moment for at in self.atoms]

    @property
    def nuclear_constraints(self):
        """The nuclear constraints for each atom."""
        return [at.constraints for at in self.atoms]

    @property
    def constraint_regions(self):
        """The constraint region for earch atom."""
        return [at.constraint_region for at in self.atoms]

    @property
    def is_empty_atoms(self):
        """If each atom is an empty atom."""
        return [at.is_empty for at in self.atoms]

    @property
    def is_pseudocore_atoms(self):
        """If each atom is a pseudocore."""
        return [at.is_pseudocore for at in self.atoms]

    @property
    def magnetic_responses(self):
        """The magnetic reponse of all atoms."""
        return [at.magnetic_response for at in self.atoms]

    @property
    def magnetic_moments(self):
        """The magnetic moments of all atoms."""
        return [at.magnetic_moment for at in self.atoms]

    @property
    def nuclear_spins(self):
        """The nuclear spin of all atoms."""
        return [at.nuclear_spin for at in self.atoms]

    @property
    def isotopes(self):
        """The isotope of all atoms."""
        return [at.isotope for at in self.atoms]

    @property
    def species_block(self):
        """Get the species block for the control.in file."""
        # TODO: this does not belong here!
        if any(sym not in self.species_dict for sym in np.unique(self.symbols)):
            raise InvalidGeometryError(
                "Species are not defined for all atoms in the structure"
            )
        return "\n".join(
            [self.species_dict[sym].content for sym in np.unique(self.symbols)]
        )

    @property
    def n_atoms(self):
        """The number of atoms in the structure."""
        return len(self.symbols)

    @property
    def masses(self) -> np.ndarray:
        """Get the masses of the structure."""
        return self._species_property("mass")

    @property
    def nuclear_charges(self) -> np.ndarray:
        """Gets the nuclear charges of the structure."""
        return self._species_property("nucleus")

    @property
    def ase_atoms(self):
        """Get the ase.atoms object for the geometry."""
        try:
            from ase.atoms import Atoms
            from ase.constraints import (
                FixAtoms,
                FixCartesian,
                FixCartesianParametricRelations,
                FixScaledParametricRelations,
            )
        except ModuleNotFoundError:
            raise ModuleNotFoundError("ASE is not installed")

        info_entries = [
            p
            for p in self._get_property_names()
            if p
            not in (
                "structure",
                "ase_atoms",
                "atoms",
                "lattice_vectors",
                "species_dict",
            )
        ]

        info_entries += [
            p
            for p in self._get_property_names(atomic=True)
            if p
            not in (
                "symbols",
                "numbers",
                "positions",
                "fractional_positions",
                "velocities",
                "initial_charges",
                "initial_moments",
                "species_block",
                "n_atoms",
                "masses",
                "nuclear_charges",
            )
        ]

        cell = self.lattice_vectors if self.lattice_vectors is not None else (0, 0, 0)

        atoms = Atoms(
            numbers=self.numbers,
            positions=self.positions,
            velocities=[v if v is not None else [0, 0, 0] for v in self.velocities],
            magmoms=self.magnetic_moments,
            charges=self.initial_charges,
            pbc=self.lattice_vectors is not None,
            cell=cell,
            info={e: getattr(self, e) for e in info_entries},
        )

        fix_params = []
        if (self.symmetry_n_params is not None) and (
            np.sum(self.symmetry_n_params) > 0
        ):
            fix_params.append(
                FixCartesianParametricRelations.from_expressions(
                    list(range(3)),
                    self.symmetry_params[: self.symmetry_n_params[0]],
                    [expr for exprs in self.symmetry_lv for expr in exprs],
                    use_cell=True,
                )
            )

            fix_params.append(
                FixScaledParametricRelations.from_expressions(
                    list(range(len(atoms))),
                    self.symmetry_params[self.symmetry_n_params[0] :],
                    [expr for exprs in self.symmetry_frac for expr in exprs],
                )
            )

        fix_cart_const = []
        fixed_atoms = []
        for index, constraint in enumerate(self.nuclear_constraints):
            if constraint is None:
                continue

            if all(constraint):
                fixed_atoms.append(index)
            elif any(constraint):
                fix_cart_const.append(FixCartesian(index, constraint))

        if len(fixed_atoms) > 0:
            fix_cart_const.insert(0, FixAtoms(fixed_atoms))

        atoms.set_constraint(fix_cart_const + fix_params)

        return atoms

    @property
    def structure(self):
        """Get the structure with no properties."""
        return self.to_structure()

    def to_structure(self,
                     properties: dict[str, Any] | None = None,
                     site_properties: dict[str, Sequence[Any]] | None = None):
        """Get the pymatgen Structure or Molecule object for the geometry."""
        properties = properties or {}
        site_properties = site_properties or {}
        try:
            from pymatgen.core import Lattice, Molecule, Structure
        except ModuleNotFoundError:
            raise TypeError("pymatgen modules not found")

        charge = np.array([atom.initial_charge for atom in self.atoms])
        magmom = np.array([atom.initial_moment for atom in self.atoms])
        velocity: list[None | list[float]] = [atom.velocity for atom in self.atoms]
        species = [atom.symbol for atom in self.atoms]
        coords = [atom.position for atom in self.atoms]

        for vv, vel in enumerate(velocity):
            if vel is not None and np.sum(np.abs(vel)) < 1e-10:
                velocity[vv] = None

        lattice = (
            Lattice(self.lattice_vectors) if self.lattice_vectors is not None else None
        )

        site_props = {"charge": charge, "magmom": magmom}
        if any(vel is not None for vel in velocity):
            site_props["velocity"] = velocity

        site_props.update(**site_properties)
        if lattice is None:
            return Molecule(species, coords, np.sum(charge),
                            properties=properties, site_properties=site_props)

        return Structure(
            lattice,
            species,
            coords,
            np.sum(charge),
            coords_are_cartesian=True,
            properties=properties,
            site_properties=site_props,
        )

    def _species_property(self, prop: str) -> np.ndarray:
        """Return an array with property values corresponding to atomic Species."""
        if any(sym not in self.species_dict for sym in np.unique(self.symbols)):
            raise InvalidGeometryError(
                "Species are not defined for all atoms in the structure"
            )
        return np.array(
            [
                getattr(self.species_dict[sym], prop) * (not self.is_empty_atoms[ss])
                for ss, sym in enumerate(self.symbols)
            ]
        )


def _create_constraints(line: list[str]) -> list[bool]:
    """Set constraints."""
    constraints = [False, False, False]
    if "x" in line[1:] or "true" in line[1:]:
        constraints[0] = True
    if "y" in line[1:] or "true" in line[1:]:
        constraints[1] = True
    if "z" in line[1:] or "true" in line[1:]:
        constraints[2] = True
    return constraints


def singular(key: str) -> str:
    """Return the singular form of a string."""
    if key[-6:] == "_atoms":
        return key[:-6]
    if key[-4:] == "sses":
        return key[:-4] + "ss"
    if key[-3:] == "ies":
        return key[:-3] + "y"
    if key[-2:] == "es":
        return key[:-2] + "e"
    if key[-1:] == "s":
        return key[:-1]
    return key
