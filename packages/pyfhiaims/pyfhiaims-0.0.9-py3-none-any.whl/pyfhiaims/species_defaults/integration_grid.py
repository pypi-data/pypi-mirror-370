"""A dataclass representing integration grid in species' defaults file."""

from collections.abc import Sequence
from dataclasses import dataclass, field

__all__ = [
    "IntegrationGrid",
]

from pyfhiaims.control.chunk import AimsControlChunk


@dataclass
class RadialIntegrationGrid(AimsControlChunk):
    r"""Radial part of integration grid.

    Parameters
    ----------
    number: int
        The total number of grid points N.
    radius: float
        The outermost shell radius $r_{outer}$ of the basic grid in \\AA.
        The location of the i-th radial shell is given by
        \\[ r_{i} = r_{outer} \\cdot \frac{1-[i/(N+1)]^2}{1-[N/(N+1)]^2} ]\
    multiplier: int
        The number of added subdivisions per basic grid spacing

    """

    number: int = field(default_factory=int)
    radius: float = field(default_factory=float)
    multiplier: int = 2
    keywords: tuple[str] = ("radial_base", "radial_multiplier")

    @classmethod
    def from_strings(cls, strings: Sequence[str]) -> "RadialIntegrationGrid":
        """Get a RadialIntegrationGrid instance from a sequence of strings."""
        num = 0
        r = 0.0
        multiplier = 2
        for line in strings:
            line = line.strip()
            if "radial_base" in line:
                num = int(line.split()[1])
                r = float(line.split()[2])
            if "radial_multiplier" in line:
                multiplier = int(line.split()[1])
        return cls(number=num, radius=r, multiplier=multiplier)

    @classmethod
    def from_string(cls, string: str) -> "RadialIntegrationGrid":
        return cls.from_strings(string.splitlines())

    def to_string(self) -> str:
        """Gt the string representation of the AngularIntegrationGrid."""
        result = [
            f"  radial_base  {self.number:4d}   {self.radius:6.4f}",
            f"  radial_multiplier   {self.multiplier:6d}",
        ]
        return "\n".join(result)


@dataclass
class AngularIntegrationGrid(AimsControlChunk):
    """Angular part of integration grid.

    Args:
    # angular: Optional[int]
    #     For self-adapting angular integration grids, the maximum allowed number of
    #     points per radial shell.
    # angular_acc: Optional[float]
    #     For self-adapting angular integration grids, specifies the desired
    #     integration accuracy for the initial Hamiltonian and overlap matrix elements
    #     Use only for cluster-type geometries, if 0 no adaptation is performed
    # angular_min: Optional[int]
    #     Specifies the minimum number of angular grid points per radial
    #     integration shell
    type: str
        Indicates how the angular integration grids (in each radial integration
        shell) for this species are determined. method is a string,
        either auto or specified.
    n_outer: int
        Specify the number of angular grid points used outside the outermost
        division radius

    """

    type: str = "specified"
    r: Sequence[float] = field(default_factory=list)
    n: Sequence[int] = field(default_factory=list)
    n_outer: int = field(default_factory=int)
    keywords: tuple[str] = (
        "angular_grids",
        "division",
        "outer_grid",
        "angular",
        "angular_acc",
        "angular_min",
    )

    def __post_init__(self):
        """Perform sanity checks on an object."""
        if len(self.r) != len(self.n):
            raise ValueError("r and n grids should be the same")

    @classmethod
    def from_strings(cls, strings: Sequence[str]) -> "AngularIntegrationGrid":
        """Get an AngularIntegrationGrid from a list of strings."""
        cls_type = "specified"
        r = []
        n = []
        n_outer = 0
        for line in strings:
            line = line.strip()
            if line.startswith("#"):
                continue
            if "angular_grids" in line:
                cls_type = line.split()[1]
            if "division" in line:
                r.append(float(line.split()[1]))
                n.append(int(line.split()[2]))
            if "outer_grid" in line:
                n_outer = int(line.split()[1])
        return cls(type=cls_type, r=r, n=n, n_outer=n_outer)

    @classmethod
    def from_string(cls, string: str) -> "AngularIntegrationGrid":
        """Get an AngularIntegrationGrid from a part of species' defaults file."""
        return cls.from_strings(string.splitlines())

    def to_string(self) -> str:
        """Get the string representation of the AngularIntegrationGrid."""
        result = [
            f"  angular_grids  {self.type}",
        ]
        for r_i, n_i in zip(self.r, self.n, strict=False):
            result.append(f"  division       {r_i:6.4f} {n_i:4d}".rstrip())
        result.append(f"  outer_grid     {self.n_outer:<4d}".rstrip())
        return "\n".join(result)


@dataclass
class IntegrationGrid(AimsControlChunk):
    """The integration grid class."""

    radial_grid: RadialIntegrationGrid
    angular_grid: AngularIntegrationGrid

    @classmethod
    def from_strings(cls, strings: Sequence[str]) -> "IntegrationGrid":
        """Get the integration grid from a list of strings."""
        radial_str = [
            s for s in strings if any(k in s for k in RadialIntegrationGrid.keywords)
        ]
        angular_str = [
            s for s in strings if any(k in s for k in AngularIntegrationGrid.keywords)
        ]
        return cls(
            radial_grid=RadialIntegrationGrid.from_strings(radial_str),
            angular_grid=AngularIntegrationGrid.from_strings(angular_str),
        )

    @classmethod
    def from_string(cls, string: str) -> "IntegrationGrid":
        """Get the integration grid from a string."""
        return cls.from_strings(string.splitlines())

    def to_string(self) -> str:
        """Get the string representation of the integration grid."""
        return "\n".join([str(self.radial_grid), str(self.angular_grid)])
