"""FHI-aims objects representing K-points (in the form of grid or list)."""

from dataclasses import dataclass
from enum import Enum


class KPointsType(Enum):
    """Enum type for Kpoints."""

    GRID = "k_grid"
    DENSITY = "k_grid_density"
    EXTERNAL = "k_points_external"


@dataclass
class AimsKPoints:
    """A base class for FHI-aims K-points representation."""

    type: KPointsType
