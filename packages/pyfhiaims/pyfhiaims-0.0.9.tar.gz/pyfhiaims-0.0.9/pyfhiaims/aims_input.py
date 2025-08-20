"""An object representing FHI-aims input.

(control.in, geometry.in, k_list.in, T_bvk.in?)
"""

from dataclasses import dataclass
from pathlib import Path

from pyfhiaims.control import AimsControl
from pyfhiaims.control.kpoints import AimsKPoints
from pyfhiaims.errors import PyaimsError
from pyfhiaims.geometry import AimsGeometry
from pyfhiaims.species_defaults.species import SpeciesDefaults


@dataclass
class AimsInput:
    """An object combining all input files for FHI-aims and providing methods
    to deal with them consistently.
    """

    control: AimsControl
    geometry: AimsGeometry = None
    species_defaults: SpeciesDefaults | dict[str, SpeciesDefaults] = None

    @classmethod
    def from_folder(cls, folder: Path | str) -> "AimsInput":
        """Get AimsInput object from a given folder."""
        if isinstance(folder, str):
            folder = Path(folder)
        if not folder.is_dir():
            raise PyaimsError("The given path is not a directory.")

        control, geometry, k_points, species_defaults = [
            None,
        ] * 4
        if (folder / "control.in").is_file():
            control = AimsControl.from_file(folder / "control.in")
        else:
            raise PyaimsError(f"No control.in file found in {folder.as_posix()}.")

        return cls(
            control,
            geometry,
        )

    @property
    def k_points(self) -> AimsKPoints:
        """The k-points for FHI-aims calculations."""
        return self.control.k_points

    @k_points.setter
    def k_points(self, k_points: AimsKPoints) -> None:
        """Setter for the k-points of an FHI-aims calculation."""
        self.control.k_points = k_points
