"""A representation of species' defaults."""

import gzip
import inspect
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path

from pyfhiaims.control.chunk import AimsControlChunk
from pyfhiaims.errors import InvalidSpeciesInput
from pyfhiaims.species_defaults.basis_function import BASIS_TYPES
from pyfhiaims.species_defaults.basis_set import BasisSet
from pyfhiaims.species_defaults.electronic_configuration import (
    IonicElectronicConfiguration,
    ValenceElectronicConfiguration,
)
from pyfhiaims.species_defaults.integration_grid import IntegrationGrid


def replace_last(line, _):
    """Get the last term on a line."""
    return line.split()[-1]


def replace_last_float(line, _):
    """Get the last float on a line."""
    return float(line.split()[-1].replace("d", "e"))


def replace_last_bool(line, _):
    """Return True if option is True."""
    return line.split()[-1] == ".true."


def replace_last_int(line, _):
    """Get the last int on a line."""
    return int(line.split()[-1])


def replace_last_float_list(line, _):
    """Return the list of floats in a line."""
    return tuple([float(ll.replace("d", "e")) for ll in line.split()[1:]])


def append_div(line, val):
    """Append new values to a division."""
    # Check this doc string
    return [*val, (float(line.split()[1].replace("d", "e")), int(line.split()[2]))]


def append_inact_div(line, val):
    """Append a new value with an inactive div."""
    # Check this doc string
    return [*val, (float(line.split()[2].replace("d", "e")), int(line.split()[3]))]


SPECIES_KEYWORD_MAP = {
    "species": ("label", replace_last),
    "mass": ("mass", replace_last_float),
    "nucleus": ("nucleus", replace_last_float),
    "l_hartree": ("l_hartree", replace_last_int),
    "cut_pot": ("cut_pot", replace_last_float_list),
    "basis_dep_cutoff": ("basis_dep_cutoff", replace_last_float),
    "basis_acc": ("basis_acc", replace_last_float),
    "cite_reference": ("cite_reference", replace_last),
    "core": ("core", lambda line, _: (int(line.split()[1]), line.split()[2])),
    "core_states": ("core_states", replace_last_int),
    "cut_atomic_basis": ("cut_atomic_basis", replace_last_bool),
    "cut_core": (
        "cut_core",
        lambda line, _: (line.split()[1], float(line.split()[2].replace("d", "e"))),
    ),
    "cut_free_atom": (
        "cut_free_atom",
        lambda line, _: (line.split()[1], float(line.split()[2].replace("d", "e"))),
    ),
    "cutoff_type": ("cutoff_type", replace_last),
    "hirshfeld_param": ("hirshfeld_param", replace_last_float_list),
    "hubbard_coefficient": ("hubbard_coefficient", replace_last_float_list),
    "include_min_basis": ("include_min_basis", replace_last_bool),
    "innermost_max": ("innermost_max", replace_last_int),
    "logarithmic": ("logarithmic", replace_last_float_list),
    "plus_u": (
        "plus_u",
        lambda line, val: (val or [])
        + [
            (
                int(line.split()[1]),
                line.split()[2],
                float(line.split()[3].replace("d", "e")),
            ),
        ],
    ),
    "plus_u_ramping": ("plus_u_ramping", replace_last_float),
    "prodbas_acc": ("prodbas_acc", replace_last_float),
    "max_n_prodbas": ("max_n_prodbas", replace_last_int),
    "max_l_prodbas": ("max_l_prodbas", replace_last_int),
    "pure_gauss": ("pure_gauss", replace_last_bool),
    "species_default_type": ("species_default_type", replace_last),
}

ALLOWED_CUTOFF_TYPES = [
    "exp(1_x)_(1-x)2",
    "junquera",
    "x2_(1-x2)",
    None,
]


VALID_INPUTS = {
    "cutoff_type": ALLOWED_CUTOFF_TYPES,
    "species_default_type": ["minimal+s", None],
    "cite_reference": ["NAO-VCC-2013", None],
    "angular_grids": ["specified", "auto"],
    "cut_free_atom": ["finite", "infinite", None],
}


@dataclass
class SpeciesDefaults:
    """Defines a species (basis set) for FHI-aims.

    Parameters
    ----------
    basis_set: BasisSet
        The basis set for the species
    # header: list[str]
    #     The header for the species file
    label: str
        The label of the species to use in the geometry.in file
    mass: float
        The nuclear mass of the species
    nucleus: float
        The charge of the species
    # division_active: Sequence[tuple[float, int]]
    #     For specified angular_grids, the number of angular points on all radial
    #     shells that are within radius, but not within another, smaller division.
    #     Restrictions: Meaningful only in a block immediately following an
    #                   angular_grids specified line.
    #     radius : Outer radius (in Å) of this division.
    #     points : Integer number of angular points requested in this division (see
    #              force_lebedev for possible values).
    # division_inactive: Sequence[tuple[float, int]]
    #     (Commented out in species file)
    #     For specified angular_grids, the number of angular points on all radial
    #     shells that are within radius, but not within another, smaller division.
    #     Restrictions: Meaningful only in a block immediately following an
    #                   angular_grids specified line.
    #     radius : Outer radius (in Å) of this division.
    #     points : Integer number of angular points requested in this division (see
    #              force_lebedev for possible values).
    l_hartree: int
        The highest angular momentum component used in the multipole expansion
        of δn(r) into δñat,lm(r) for the present species.
    cut_pot: Vector3D
        Specifies the numerical parameters for the general (default) confinement
        potential vc(r) for all basis functions of this species.
            onset: specifies the default onset radius of the cutoff potential,
                   in Å (vc(r)=0 for r < r_onset).
            width: specifies the radial width w of the cutoff potential,
                   in Å (vc(r)=∞ for r > r_onset + w).
            scale: is a scaling parameter to increase or decrease the numerical
                   value of vc
    basis_dep_cutoff: bool | float
        Basis function dependent adjustment of the confinement potential for
        this species. If not .false., the onset of the basis confining potential
        (see cut_pot) is adjusted separately for each basis function, such that
        the norm of this basis function outside r_onset is smaller that threshold.
        The maximum possible onset radius is still given by the value explicitly
        specified by cut_pot
    basis_acc: float
        Technical cutoff criterion for on-site orthonormalization of radial
        functions. If initial normalization is below this value it is omitted
    cite_reference: str
        Triggers the addition of a specific citation to the end of the FHI-aims
        standard output for a given run. Given a key
    core: tuple[int, str]
        Defines the top “core” shell of the species for this angular momentum.
            n: radial quantum number
            l: character specifying angular momentum (s, p, d, f, ....)
        (experimental)
    core_states: int
        Number of core states (2 * core_states = number of core electrons)
        0 means don't use. This will interact with core in the future (experimental)
    cut_atomic_basis: bool
        If True basis_dep_cutoff keyword also applies to atomic-type (minimal)
        radial functions
    cut_core: tuple[str, float]
        Deprecated
        Can be used to define a separate (tighter) onset of the cutoff potential for
        all core radial functions.
        type : A string, either finite or infinite. Default: finite .
        radius : A real number, in Å: Onset radius for the cutoff potential,
                 as defined in the cut_pot tag. Default: same as onset in cut_pot .
    cut_free_atom: tuple[str, float]
        Adds a cutoff potential to the initial, non-spinpolarized free-atom
        calculation that yields free-atom densities and potentials for many basic
        tasks.
        type: either finite or infinite
        radius: A real number, in Å: Onset radius for the cutoff potential, as defined
                in the cut_pot tag
    cutoff_type: str
        Specifies the functional form of the confinement potential associated
        with this species
    hirshfeld_param: tuple[float, float, float]
        To explicitly allow setting the parameters for the Tkatchenko-Scheffler
        van der Waals correction. Does not apply to the vdw_ts keyword.
        C6 alpha R0 (See FHI-aims manuel)
    hubbard_coefficient: tuple[float, float, float, float]]
        See FHI-aims manuel, experimental feature for DFT + U
    include_min_basis: bool
        If False exclude the minimal basis of numerically tabulated free-atom
        basis functions (core and valence) from the basis set
    innermost_max: int
        If, after on-site orthonormalization, a radial function’s innermost extremum
        is inside the radial grid shell number, counting from the nucleus, that radial
        function is rejected in order to prevent inaccurate integrations.
    logarithmic: tuple[float, float, float]]
        Defines the dense one-dimensional “logarithmic” grid for the direct solution
        of all radial equations (free atom quantities, Hartree potential).
        r_min: is a real number (in bohr); the innermost point of the logarithmic grid
               is defined as r(1)=r_min/Z, where Z is the atomic number of the nucleus
               of the species . Default: 0.0001 bohr.
        r_max: is a real number (in bohr), the outermost point of the logarithmic grid,
               r(N). Default: 100 bohr.
        increment: is a real number, the increment factor α between successive
                   grid points, r(i) = α · r(i − 1). Default: 1.0123.
    # outer_grid: int
    #     Specify the number of angular grid points used outside the outermost
    #     division radius
    plus_u: Sequence[tuple[int, str, float]]
        Experimental—only for DFT+U. Adds a +U term to one specific shell
        of this species.
            n: the (integer) radial quantum number of the selected shell.
            l: is a character, specifying the angular momentum ( s, p, d, f, ...)
               of the selected shell.
            U: the value of the U parameter, specified in eV.
    prodbas_acc: float
        Technical cutoff criterion for on-site orthonormalization of auxiliary radial
        functions.
    max_l_prodbas: int
        Specifies the maximal angular quantum number for the auxiliary (product) basis
        function. Any possible auxiliary basis with an angular momentum higher than
        max_l_prodbas is excluded.
    max_n_prodbas: int
        Specifies the maximal principal quantum number for the regular basis
        function to be included in the auxiliary (product) basis construction
    pure_gauss: bool
        If True any Gaussian basis functions for this species will be purely
        spherical Gaussians
    # radial_multiplier: int]
    #     Systematically increases the radial integration grid density.
    #     number specifying the number of added subdivisions per basic grid spacing.
    species_default_type: str]
        Defines the default type of basis set

    """

    label: str = None
    mass: float = None
    nucleus: float = None
    l_hartree: int = None
    integration_grid: IntegrationGrid = None
    valence_config: ValenceElectronicConfiguration = None
    ionic_config: IonicElectronicConfiguration = None
    basis_set: BasisSet = None

    basis_dep_cutoff: bool | float = 1e-4
    cut_pot: tuple[float, float, float] = field(default_factory=tuple)
    basis_acc: float = None
    cite_reference: str = None
    core: tuple[int, str] = None
    core_states: int = None
    cut_atomic_basis: bool = None
    cut_core: tuple[str, float] = None
    cut_free_atom: tuple[str, float] = None
    cutoff_type: str = None
    hirshfeld_param: tuple[float, float, float] = None
    hubbard_coefficient: tuple[float, float, float, float] = None
    include_min_basis: bool = None
    innermost_max: int = None
    logarithmic: tuple[float, float, float] = None
    plus_u: Sequence[tuple[int, str, float]] = None
    prodbas_acc: float = None
    max_l_prodbas: int = None
    max_n_prodbas: int = None
    pure_gauss: bool = None
    species_default_type: str = None

    header: str | None = None

    def __post_init__(self):
        """Verify all inputs passed via init."""
        message = ""
        for key, val in asdict(self).items():
            if (
                key in VALID_INPUTS
                and (val if not isinstance(val, Sequence) else val[0])
                not in VALID_INPUTS[key]
            ):
                message += (
                    f"The input for key {key} ({val}) is invalid. "
                    f"Valid options are {VALID_INPUTS[key]}\n"
                )
        if len(message) != 0:
            raise InvalidSpeciesInput(message)

    def __str__(self):
        return self.content

    @property
    def content(self):
        """Get the text block for the species."""
        dct = asdict(self)
        for key in (
            "header",
            "basis_set",
            "integration_grid",
            "valence_config",
            "ionic_config",
        ):
            dct.pop(key)

        file_contents = [
            f"{self.header}",
            f"  species               {dct.pop('label')}",
            "#     global species definitions",
            f"  nucleus               {dct.pop('nucleus')}",
            f"  mass                  {dct.pop('mass')}",
            "#",
            f"  l_hartree             {dct.pop('l_hartree')}",
            "#",
        ]
        cut_pot = dct.pop("cut_pot")
        file_contents += [
            f"  cut_pot               {cut_pot[0]} {cut_pot[1]} {cut_pot[2]}",
            f"  basis_dep_cutoff      {dct.pop('basis_dep_cutoff')}",
            "#",
            f"{self.integration_grid}",
        ]

        if any(val is not None for val in dct.values()):
            file_contents += [
                "#" * 82,
                "#",
                "# Optional basis settings passed to pyfhiaims",
                "#",
                "#" * 82,
            ]
            for key, val in dct.items():
                if val is None:
                    continue

                if key == "plus_u":
                    for pu in val:
                        file_contents.append(
                            f"    {key:<10s}{' '.join([str(v) for v in pu])}"
                        )
                elif isinstance(val, tuple):
                    file_contents.append(
                        f"  {key:<22s}{' '.join([str(v) for v in val])}"
                    )
                else:
                    file_contents.append(f"  {key:<22s}{val}")

        file_contents += [
            "#" * 82,
            "#",
            '#  Definition of "minimal" basis',
            "#",
            "#" * 82,
            "#     valence basis states",
            f"{self.valence_config}",
            "#     ion occupancy",
            f"{self.ionic_config}",
        ]

        file_contents += [
            "#" * 82,
            "#",
            "#  Suggested additional basis functions. For production calculations,",
            "#  uncomment them one after another "
            "(the most important basis functions are",
            "#  listed first).",
            "#",
            "#  These were set using pyfhiaims, "
            "original may files have additional comments",
            "#",
            "#" * 82,
        ]

        file_contents.append(f"{self.basis_set}")
        return "\n".join(file_contents)

    @classmethod
    def from_file(cls, filename: str | Path) -> "SpeciesDefaults":
        """Create a species from an FHI-aims species file."""
        lines = None
        for fname in [filename, f"{filename}.gz"]:
            if not Path(fname).exists():
                continue

            if fname[-3:] == ".gz":
                with gzip.open(fname, mode="rt") as in_file:
                    lines = in_file.readlines()
            else:
                with open(fname) as in_file:
                    lines = in_file.readlines()
        if lines is None:
            raise FileNotFoundError(f"Species file {filename} does not exit.")
        return cls.from_strings(lines)

    @classmethod
    def from_strings(cls, config_str: list[str]) -> "SpeciesDefaults":
        """Create a species from a list of lines from a file with species' defaults.

        The keywords from the species' defaults are organized in logical chunks to
        facilitate comparing between two different SpeciesDefaults objects.

        Parameters
        ----------
        cls:
            The class keyword
        config_str: list[str]
            a list of strings from the species' defaults.

        Returns
        -------
        SpecieseDefaults
            The object defined by the strings from the final

        """
        parameters = {}
        # get the keywords pertaining to chunk objects
        kw_map = {}
        # as well as class objects for chunks
        chunk_types = {}
        for f in fields(cls):
            if inspect.isclass(f.type) and issubclass(f.type, AimsControlChunk):
                for kw in f.type.keywords:
                    kw_map[kw] = f.name
                chunk_types[f.name] = f.type
                parameters[f.name] = []

        lines = [line.strip() for line in config_str]

        for il, line in enumerate(lines):
            if len(line) == 0:
                continue
            split_line = line.split()
            if (len(split_line) <= 1) and (split_line[0] == "#"):
                continue

            if split_line[0] != "#":
                key = split_line[0]
            else:
                key = f"{split_line[0]} {split_line[1]}"

            if key in SPECIES_KEYWORD_MAP:
                param_setter = SPECIES_KEYWORD_MAP[key]
                cur_val = parameters.get(param_setter[0], None)
                parameters[param_setter[0]] = param_setter[1](line, cur_val)
                continue
            # get chunk lines
            if key in kw_map:
                parameters[kw_map[key]].append(line)

            # basis functions appear below
            if key in BASIS_TYPES:
                parameters["basis_set"] = BasisSet.from_string("\n".join(lines[il:]))
                break
        for chunk, chunk_type in chunk_types.items():
            parameters[chunk] = chunk_type.from_strings(parameters[chunk])

        header_lines = []
        if "########" in lines[0]:
            header_lines.append(lines[0])
            il = 1
            while len(lines[il]) == 0 or lines[il][0] == "#":
                header_lines.append(lines[il])
                il += 1
            parameters["header"] = "\n".join(header_lines)
        else:
            parameters["header"] = "\n".join(
                [
                    "",
                    "#" * 82,
                    "#",
                    f"# Read in species defaults for {parameters['label']}"
                    f" atom from pyfhiaims",
                    "#",
                    "#" * 82,
                ]
            )

        return cls(**parameters)
