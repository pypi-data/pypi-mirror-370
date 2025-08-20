"""An object representing parse results of FHI-aims standard output."""

import os.path
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any

from pyfhiaims.errors import AimsParseError
from pyfhiaims.geometry import AimsGeometry
from pyfhiaims.outputs.parser import StdoutParser
from pyfhiaims.outputs.parser.utils import NamedDict

CONVERGED_RESULTS_KEYS = [
    "total_energy",
    "free_energy",
    "forces",
    "stress",
    "stresses",
    "magmom",
    "dipole",
    "fermi_energy",
    "n_scf_iter",
    "mulliken_charges",
    "mulliken_spins",
    "hirshfeld_charges",
    "hirshfeld_dipole",
    "hirshfeld_volumes",
    "hirshfeld_atomic_dipoles",
    "dielectric_tensor",
    "polarization",
    "vbm",
    "cbm",
    "gap",
    "direct_gap",
    "pressure",
]


@dataclass
class AimsImage:
    """Object to represent the aims outputs."""

    _geometry: AimsGeometry = None
    _results: dict[str, Any] = field(default=dict)
    _scf: list[dict[str, Any]] = field(default=list)
    _converged: bool = None

    @classmethod
    def from_spec(cls, ionic_spec: dict[str, Any]):
        """Get the image from the image spec."""
        scf = ionic_spec.pop("scf_steps", [])
        if scf:
            spec = {k: v for k, v in scf[-1].items() if "change" not in k}
        else:
            warnings.warn(UserWarning("No SCF steps found"), stacklevel=2)
            spec = {}

        spec.update(ionic_spec)

        geometry = spec.pop("geometry", None)
        converged = spec.pop("scf_converged", False)

        results: dict[str, Any] = {
            key.replace("atomic_", ""): spec.get(key) for key in spec
        }

        if (geometry and geometry.lattice_vectors is not None
                and spec.get("is_metallic", False)):
            spec["total_energy"] = results["total_energy"]
            results["total_energy"] = spec.get("corrected_total_energy")

        results["n_scf_iter"] = len(scf)
        results["magmom"] = spec.get("spin")
        results["fermi_energy"] = spec.get("chemical_potential")
        results["stress"] = spec.get(
            "analytical_stress", spec.get("numerical_stress")
        )
        results["dipole"] = spec.get("total_dipole_moment")
        results["absolute_dipole"] = spec.get("absolute_dipole_moment")
        results["energy"] = results["free_energy"]

        return cls(
            _geometry=geometry,
            _results=results,
            _scf=scf,
            _converged=converged,
        )

    def __post_init__(self):
        """Check if lattice exists, and if so make fractional coords."""
        if self._geometry and self._geometry.lattice_vectors is not None:
            for atom in self._geometry.atoms:
                atom.set_fractional(self._geometry.lattice_vectors)

    def __getitem__(self, key: str) -> Any:
        """Get a particular result."""
        try:
            return self._results[key]
        except KeyError:
            if key in CONVERGED_RESULTS_KEYS:
                return None
            raise ValueError(f"Requested item ({key}) is not a parsable result")

    def __getattr__(self, name: str) -> Any:
        """Get a particular result for the result."""
        return self[name]

    @property
    def geometry(self):
        """Return the geometry of the calculation."""
        return self._geometry

    @property
    def converged(self):
        """Return True if calculation is converged."""
        return self._converged

    def get_results(self, verbosity: str = "converged") -> dict[str, Any]:
        """Return the results dictionary."""
        if verbosity not in ["converged", "all"]:
            raise ValueError(
                f"verbosity must be one of 'converged' or 'all', not {verbosity}"
            )
        if verbosity == "converged":
            return {k: v for k, v in self._results.items()
                    if k in CONVERGED_RESULTS_KEYS}
        self._results["scf_steps"] = self._scf
        return self._results

    @property
    def results(self):
        """Return the results dictionary."""
        return self.get_results(verbosity="converged")

    @property
    def scf(self):
        """Return the SCF data."""
        return self._scf


class AimsStdout:
    """The standard output parser and results handler for FHI-aims calculations.

    This class is responsible for parsing the output file of an FHI-aims calculation
    and storing the extracted results in a structured format. It facilitates access
    to parsed results, metadata, warnings, and errors associated with the calculation.

    Attributes:
        file_name (str): The full path to the FHI-aims output file being processed.

    Methods:
        results (dict[str, Any]): Provides parsed results for FHI-aims calculation.
        metadata (NamedDict[str, Any]): Provides runtime choices and background
            calculation metadata.
        warnings (list[str]): Retrieves warning messages found in the output file.
        errors (list[str]): Retrieves error messages from the output, typically at the
            end of the file.
        is_finished_ok (bool): Checks if the calculation finished successfully.
        __getattr__: Allows accessing results dictionary
            attributes as object attributes.
        keys (set[str]): Retrieves the set of all keys present in the output object.

    Raises:
        FileNotFoundError: If the specified output file does not exist.
        AimsParseError: If the output file is not a valid FHI-aims output.

    """

    def __init__(
        self,
        stdout_file: str | Path | IO,
        parser: StdoutParser = None,
    ):
        """Construct AimsStdout.

        Args:
            stdout_file (str | Path | IO): The output file
            parser (StdoutParser, optional): The parser to use.

        """
        if isinstance(stdout_file, str | Path):
            self.file_name = Path(stdout_file).resolve().as_posix()
            file_path = Path(stdout_file)
            if not file_path.is_file():
                raise FileNotFoundError(
                    f"FHI-aims output file {self.file_name} does not exist"
                )
        else:
            self.file_name = os.path.realpath(stdout_file.name)
        self._parser = parser or StdoutParser(stdout_file)
        self._results = self._parser.parse()

        # gather the parsed results into one place, like in ASE parser by Tom
        if "aims_version" not in self._results:
            raise AimsParseError(
                f"{self.file_name} is not a valid FHI-aims output file"
            )

        if len(self._results.get("ionic_steps", [])) > 0:
            ionic_steps = self._results["ionic_steps"]
        else:
            warnings.warn(
                UserWarning("FHI-aims calculation did not start"), stacklevel=2
            )
            ionic_steps = []

        specs = [spec.copy() for spec in ionic_steps]

        if len(specs) > 0:
            if self.metadata.get("relax") or self.metadata.get("calculate_atom_bsse"):
                for ii in range(1, len(specs)):
                    specs[ii]["geometry"] = specs[ii - 1]["geometry"]

            init_geo = AimsGeometry.from_strings(
                self._results["input"]["geometry_in"].splitlines()
            )
            if init_geo.lattice_vectors is not None:
                for atom in init_geo.atoms:
                    atom.set_fractional(init_geo.lattice_vectors)
            specs[0]["geometry"] = init_geo

        if "final" not in self._results:
            self._results["final"] = {}

        if "time" in self._results:
            self._results["final"]["cpu_time"] = self._results["time"]["total"][0]
            self._results["final"]["total_time"] = self._results["time"]["total"][1]

        self._results["final"]["dielectric_tensor"] = None
        if "dfpt" in self._results:
            self._results["final"]["dielectric_tensor"] = self._results["dfpt"][
                "dielectric_tensor"
            ]
        if len(specs) > 0:
            specs[-1].update(self.final)
        # this is not a good style, as AimsStdout should not depend on Image
        # also, this is just erroneous, as there are a lot of situations
        # when the result is not trajectory-like, e.g. numerical stress calculation
        self._images = [AimsImage.from_spec(spec) for spec in specs]
        if len(self._images) > 0:
            self._results["final"].update(self._images[-1].results)

    @property
    def results(self) -> dict[str, Any]:
        """A dictionary with results for FHI-aims calculation."""
        return self._results

    @property
    def images(self) -> list[AimsImage]:
        """Get all images in the file."""
        return self._images

    @property
    def n_images(self) -> int:
        """Get all images in the file."""
        return len(self._images)

    @property
    def metadata_summary(self) -> dict[str, Any]:
        """Summarize metadata into a single object."""
        return {
            "commit_hash": self._results.get("commit_hash"),
            "aims_uuid": self._results.get("aims_uuid"),
            "version_number": self._results.get("aims_version"),
            "fortran_compiler": self._results.get("fortran_compiler", "").split("/")[
                -1
            ],
            "c_compiler": self._results.get("c_compiler", "").split("/")[-1],
            "fortran_compiler_flags": self._results.get("fortran_compiler_flags"),
            "c_compiler_flags": self._results.get("c_compiler_flags"),
            "build_type": self._results.get("build_type"),
            "linked_against": self._results.get("linked_against"),
        }

    @property
    def header_summary(self) -> dict[str, Any]:
        """Summarize the initial structure into a single object."""
        init_geo = AimsGeometry.from_strings(
            self._results["input"]["geometry_in"].splitlines()
        )
        return {
            "initial_geometry": init_geo,
            "initial_lattice": init_geo.lattice_vectors,
            "is_relaxation": self.metadata.relax,
            "is_md": self.metadata.md,
            "n_atoms": self.metadata.num_atoms,
            "n_bands": self.metadata.num_bands,
            "n_electrons": int(self.metadata.num_electrons),
            "n_spins": self.metadata.num_spins,
            "electronic_temperature": self._results.get("electronic_temperature", 0.0),
            "n_k_points": self.metadata.get("num_k_points"),
            "k_points": self._results.get("k_points"),
            "k_point_weights": self._results.get("k_point_weights"),
        }

    def get_image(self, ind: int) -> AimsImage:
        """Get the image at index ind."""
        return self._images[ind]

    @property
    def metadata(self) -> NamedDict[str, Any]:
        """A metadata dictionary for FHI-aims calculation,
        including runtime choices and some background calculation checks.
        """
        return NamedDict(self._parser.run_metadata)

    @property
    def warnings(self) -> list[str]:
        """A list of warning messages for FHI-aims calculation.

        A warning message is the one beginning with an optional space and one or
        several asterisks.
        """
        return self._parser.warnings

    @property
    def errors(self) -> list[str]:
        """A list of error messages for FHI-aims calculation.

        An error message is a warning at the end of the file.
        """
        return self._parser.errors

    @property
    def is_finished_ok(self) -> bool:
        """A check if the calculation is finished successfully."""
        return self._results.get("is_finished_ok", False)

    def __getitem__(self, ind: int) -> AimsImage:
        """Get an image."""
        return self.get_image(ind)

    def __len__(self) -> int:
        """Get n_images."""
        return self.n_images

    def __getattr__(self, item) -> Any:
        """Get a value for a specific item."""
        if item in self._results["final"]:
            return self._results["final"][item]
        if item in self._results:
            return self._results[item]
        return None

    def keys(self) -> set[str]:
        """Return the keys present in the output object."""
        return set(
            list(self._results.get("final", {}).keys())
            + list(self._results.keys())
            + ["metadata", "warnings", "errors"]
        )
