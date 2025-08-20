"""Classes for reading/manipulating/writing FHI-aims control.in files."""

from __future__ import annotations

import re
import time
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from warnings import warn

import numpy as np
from monty.json import MontyDecoder, MSONable

from pyfhiaims.errors import PyaimsError
from pyfhiaims.geometry.geometry import AimsGeometry
from pyfhiaims.species_defaults.species import SpeciesDefaults

if TYPE_CHECKING:
    from typing import Any, Self, TextIO

    from ase import Atoms
    from pymatgen.core import Molecule, Structure

    from pyfhiaims.control.kpoints import AimsKPoints

__author__ = "Thomas A. R. Purcell"
__version__ = "1.0"
__email__ = "purcellt@arizona.edu"
__date__ = "July 2024"


@dataclass
class AimsControl(MSONable):
    """An FHI-aims control.in file.

    Attributes:
        parameters (dict[str, Any]): The parameters' dictionary containing all input
            flags (key) and values for the control.in file

    """

    parameters: dict[str, Any] = field(default_factory=dict)
    outputs: list[str] = field(default_factory=list)
    k_points: AimsKPoints = None
    species_defaults: dict[str, SpeciesDefaults] = field(default_factory=dict)  # None?

    def __getitem__(self, key: str) -> Any:
        """Get an input parameter.

        Args:
            key (str): The parameter to get

        Returns:
            The setting for that parameter

        Raises:
            KeyError: If the key is not in self._parameters

        """
        if key == "output":
            return self.outputs

        if key not in self.parameters:
            raise KeyError(f"{key} not set in AimsControl")
        return self.parameters[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an attribute of the class.

        Args:
            key (str): The parameter to get
            value (Any): The value for that parameter

        """
        if key == "output":
            warn(
                "Outputs are set seperately, use the outputs property",
                RuntimeWarning,
                stacklevel=1,
            )
        else:
            self.parameters[key] = value

    def __delitem__(self, key: str) -> Any:
        """Delete a parameter from the input object.

        Args:
        key (str): The key in the parameter to remove

        Returns:
            Either the value of the deleted parameter or None if key is
            not in self._parameters

        """
        if key == "output":
            self.outputs = []

        return self.parameters.pop(key, None)

    @staticmethod
    def get_aims_control_parameter_str(key: str, value: Any, fmt: str) -> str:
        """Get the string needed to add a parameter to the control.in file.

        Args:
            key (str): The name of the input flag
            value (Any): The value to be set for the flag
            fmt (str): The format string to apply to the value

        Returns:
            str: The line to add to the control.in file

        """
        if value is None:
            return ""
        return f"{key:50s}{fmt % value}\n"

    def get_content(
        self,
        geometry: AimsGeometry | Atoms | Structure | Molecule,
        verbose_header: bool = False,
    ) -> str:
        """Get the content of the file.

        Args:
            geometry: The geometry to write the input file for
            verbose_header (bool): If True print the input option dictionary

        Returns:
            str: The content of the file for a given geometry

        """
        parameters = deepcopy(self.parameters)

        if geometry.__class__.__name__ == "Atoms":
            geometry = AimsGeometry.from_atoms(geometry)
        elif geometry.__class__.__name__ in ("Structure", "Molecule"):
            geometry = AimsGeometry.from_structure(geometry)

        lim = "#" + "=" * 79
        content = ""
        cubes = parameters.pop("cubes", [])

        if verbose_header:
            content += "#\n# List of parameters used to initialize the calculator:\n"
            for param, val in parameters.items():
                content += f"#     {param}:{val}\n"
            content += f"#     output:{self.outputs}\n"
            content += f"{lim}\n"

        if parameters["xc"] == "LDA":
            parameters["xc"] = "pw-lda"

        tiers = parameters.pop("tier", None)
        plus_u = parameters.pop("plus_u", None)
        species_dir = parameters.pop("species_dir", None)

        if isinstance(tiers, int):
            tiers = dict.fromkeys(np.unique(geometry.symbols), tiers)
        elif tiers is not None:
            assert all(sym in tiers for sym in np.unique(geometry.symbols))

        # Don't override species defaults
        if species_dir is not None and Path(species_dir).exists():
            geometry.load_species(species_directory=species_dir)

        for sym in np.unique(geometry.symbols):
            if tiers is not None:
                end_activate = 1 + min(
                    tiers[sym], geometry.species_dict[sym].basis_set.n_tiers
                )
                for tt in range(1, end_activate):
                    geometry.species_dict[sym].basis_set.activate_tier(tt)

                for tt in range(
                    end_activate, geometry.species_dict[sym].basis_set.n_tiers + 1
                ):
                    geometry.species_dict[sym].basis_set.deactivate_tier(tt)

            if plus_u is not None:
                geometry.species_dict[sym].plus_u = plus_u.get(sym)

        if all(inp in parameters for inp in ["smearing", "occupation_type"]):
            raise ValueError(
                "Both smearing and occupation_type can't be "
                "in the same parameters file."
            )

        for key, value in parameters.items():
            if key == "smearing":
                name = parameters["smearing"][0].lower()
                if name == "fermi-dirac":
                    name = "fermi"
                width = parameters["smearing"][1]
                if name == "methfessel-paxton":
                    order = parameters["smearing"][2]
                    order = f"{order:d}"
                else:
                    order = ""

                content += self.get_aims_control_parameter_str(
                    "occupation_type", (name, width, order), "%s %f %s"
                )
            elif key == "vdw_correction_hirshfeld" and value:
                content += self.get_aims_control_parameter_str(key, "", "%s")
            elif key == "xc":
                if "libxc" in value:
                    warn(
                        f"Not all libxc functionals will work with FHI-aims "
                        f"be careful when using {value}",
                        stacklevel=1,
                    )
                    content += self.get_aims_control_parameter_str(
                        "override_warning_libxc", ".true.", "%s"
                    )
                content += self.get_aims_control_parameter_str(key, value, "%s")
            elif isinstance(value, bool):
                content += self.get_aims_control_parameter_str(
                    key, str(value).lower(), ".%s."
                )
            elif isinstance(value, tuple | list):
                content += self.get_aims_control_parameter_str(
                    key, " ".join(map(str, value)), "%s"
                )
            elif isinstance(value, str):
                content += self.get_aims_control_parameter_str(key, value, "%s")
            else:
                content += self.get_aims_control_parameter_str(key, value, "%r")

        for output_type in self.outputs:
            content += self.get_aims_control_parameter_str("output", output_type, "%s")

        if cubes:
            for cube in cubes:
                content += cube.control_block

        content += f"{lim}\n\n"

        for sp in geometry.species_dict.values():
            content += sp.content

        return content

    def write_file(
        self,
        geometry: AimsGeometry,
        writer: str | Path | TextIO | None = None,
        header: str | None = None,
        verbose_header: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Write the control.in file.

        Args:
            geometry (AimsGeometry): The structure to write the input
                file for
            writer (str | Path | TextIO): The directory to write the control.in file.
                If None use cwd
            header (str | None): An optional header to add to the file
            verbose_header (bool): If True print the input option dictionary
            overwrite (bool): If True allow to overwrite existing files

        Raises:
            ValueError: If a file must be overwritten and overwrite is False
            ValueError: If k-grid is not provided for the periodic structures

        """
        writer = writer or Path.cwd()
        if isinstance(writer, str | Path):
            if (Path(writer) / "control.in").exists() and not overwrite:
                raise ValueError(f"control.in file already in {writer}")
            fname = f"{writer}/control.in"
        else:
            try:
                fname = writer.name
            except AttributeError:
                fname = "control.in"
        if header is None:
            header = "\n".join(
                [
                    f"#{'=' * 79}\n",
                    f"# FHI-aims control file: {fname}\n",
                    f"# {time.asctime()}\n",
                    f"#{'=' * 79}\n",
                ]
            )

        if (geometry.lattice_vectors is not None) and (
            "k_grid" not in self.parameters and "k_grid_density" not in self.parameters
        ):
            raise ValueError("k-grid must be defined for periodic systems")

        content = header + self.get_content(geometry, verbose_header)

        if isinstance(writer, str | Path):
            with open(fname, mode="w") as file:
                file.write(content)
        else:
            writer.write(content)

    def as_dict(self) -> dict[str, Any]:
        """Get a dictionary representation of the control.in file."""
        dct: dict[str, Any] = {
            "@module": type(self).__module__,
            "@class": type(self).__name__,
            "parameters": self.parameters,
            "outputs": self.outputs,
        }
        return dct

    @classmethod
    def from_strings(csl, content_str: str) -> AimsControl:
        """Generate control.in file from its content str."""
        parameters = {}
        outputs = []

        # get species' defaults from the file first
        species = {}
        species_re = re.compile(r"(?<=\n) *species.*?(?=\n *species|$)", re.DOTALL)
        species_lines = re.findall(species_re, content_str)
        element_re = re.compile(r" *species *(\S+)", re.DOTALL)

        for block in species_lines:
            if re.match(element_re, block) is not None:
                element = re.match(element_re, block).group(1)
                species[element] = SpeciesDefaults.from_strings(block.split("\n"))

        # then everything else
        for line in content_str.splitlines():
            # remove comments and blank lines
            idx = line.find("#")
            line = line.strip() if idx == -1 else line[:idx].strip()
            if not line:
                continue
            # stop at species
            if line.startswith("species "):
                break
            k, v = line.split(maxsplit=1)
            if k == "output":
                if "cube" in v:
                    # TODO: does not work with Cubes yet
                    raise PyaimsError(
                        "Reading control.in from file does not work with cubes yet"
                    )
                outputs.append(v)
            else:
                parameters[k] = v

        return AimsControl(
            parameters=parameters, outputs=outputs, species_defaults=species
        )

    @classmethod
    def from_file(cls, control_file: str | Path) -> AimsControl:
        """Instantiate the Control object."""
        with open(control_file) as f:
            lines = f.read()

        return cls.from_strings(lines)

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> Self:
        """Initialize from dictionary.

        Args:
            dct (dict[str, Any]): The MontyEncoded dictionary

        Returns:
            The AimsControl for dct

        """
        decoded = {
            key: MontyDecoder().process_decoded(val)
            for key, val in dct.items()
            if not key.startswith("@")
        }

        return cls(parameters=decoded["parameters"], outputs=decoded["outputs"])
