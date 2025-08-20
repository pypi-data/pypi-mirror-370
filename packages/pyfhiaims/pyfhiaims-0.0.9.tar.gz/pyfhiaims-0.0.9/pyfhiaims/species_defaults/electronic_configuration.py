"""Electronic configurations for the FHI-aims species' defaults."""

from dataclasses import dataclass, field
from enum import Enum

from pyfhiaims.control.chunk import AimsControlChunk


class Orbital(Enum):
    """Enum mapping l quantum number to letter."""

    S = 0
    P = 1
    D = 2
    F = 3
    G = 4
    H = 5
    I = 6


class ElectronicConfigurationType(Enum):
    """Enumb mapping valence and ion occ orbitals."""

    VALENCE = "valence"
    IONIC = "ion_occ"


@dataclass
class ElectronicConfiguration(AimsControlChunk):
    """Electronic configuration, both valence and ionic."""

    type: ElectronicConfigurationType = None
    occupations: dict[(int, Orbital):int] = field(default_factory=dict)

    @classmethod
    def from_strings(cls, config_str) -> "ElectronicConfiguration":
        """Get the electronic configuration from a multi-line string."""
        config_type = None
        config = {}
        for line in config_str:
            type_str, n, l, occ = line.split()
            if config_type is None:
                config_type = ElectronicConfigurationType(type_str)
            elif config_type != ElectronicConfigurationType(type_str):
                raise ValueError("config_type is inconsistent with type_str")
            config[(int(n), Orbital[l.upper()])] = int(float(occ))
        return cls(
            type=config_type,
            occupations=config,
        )

    @property
    def n_electrons(self) -> int:
        """The number of electrons in the given configuration."""
        num = 0
        for k, v in self.occupations.items():
            n, l = k
            num += (n - l.value - 1) * (4 * l.value + 2) + v
        return num

    def to_string(self) -> str:
        """Get the string representation of the configuration."""
        return "\n".join(
            [
                f"{self.type.value:>11} {k[0]:6d}  {k[1].name.lower()} {v:3d}."
                for k, v in self.occupations.items()
            ]
        )


class ValenceElectronicConfiguration(ElectronicConfiguration):
    """Valence electron basis function definition."""

    type = ElectronicConfigurationType.VALENCE
    keywords = ("valence",)


class IonicElectronicConfiguration(ElectronicConfiguration):
    """The ionic occupation basis function definition."""

    type = ElectronicConfigurationType.IONIC
    keywords = ("ion_occ",)
