"""Definition of the Basis Function class."""

from __future__ import annotations

import inspect
import sys
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class BasisFunctionError(Exception):
    """Exception raised if an error occurs when parsing an Aims output file."""


@dataclass(kw_only=True)
class BasisFunction:
    """Defines an FHI-aims basis function.

    Parameters
    ----------
    n: int
        Radial quantum number
    l: str
        The angular momentum of the function
    type: str
        A type of basis function (from `hydro`, `ionic`, `confined`, `sto`, `gaussian`)
    enabled: bool
        A flag indicating if the basis function is enabled (not commented out
    aux: bool
        A flag indicating if the basis function belongs to the auxiliary basis set used
        to expand Coulomb operator

    """

    n: int
    l: str | int
    type: str
    enabled: bool = True
    aux: bool = False
    comments: list[str] | None = None

    def content_block(self, content_fields: Sequence[str]) -> str:
        """Get the content block for the control.in file."""
        content = [str(getattr(self, f)) for f in content_fields]
        return (
            f"{'#' if not self.enabled else ' '} "
            f"{('for_aux' if self.aux else ''):>7}{self.type:>9} "
            f"{self.n:6d}  {self.l}  {' '.join(content)}"
            f"{'' if self.comments is None else ' #' + self.comments[0]}"
        )

    @classmethod
    def from_string(cls, string: str) -> BasisFunction:
        """Get the general BasisFunction object from string representation."""
        string = string.strip()
        enabled = not string.startswith("#")
        if not enabled:
            string = "\n".join([line.strip()[1:] for line in string.split("\n")])
        for_aux = "aux" in string
        comments = None

        if "#" in string:
            comments = [
                "" if "#" not in line else "#".join(line.strip().split("#")[1:])
                for line in string.split("\n")
            ]
            string = "\n".join(
                [line.split("#")[0].strip() for line in string.split("\n")]
            )

        if for_aux:
            if "gaussian" in string:
                string = string.replace("aux_", "")
            else:
                string = string.replace("for_aux", "")

        for k, v in BASIS_TYPES.items():
            if k in string:
                basis_function = v.from_string(string)
                basis_function.enabled = enabled
                basis_function.aux = for_aux
                basis_function.comments = comments
                return basis_function
        raise ValueError(f"No valid basis function type found in {string}")


@dataclass(kw_only=True)
class HydroBasisFunction(BasisFunction):
    """The Hydrogen like basis function for FHI-aims.

    Parameters
    ----------
    z_eff: float
        scales the radial function as an effective nuclear charge in the defining
        Coulomb potential zeff/r.

    """

    z_eff: float
    type: str = "hydro"

    @classmethod
    def from_string(cls, string: str) -> HydroBasisFunction:
        """Get HydroBasisFunction object from string representation."""
        enabled = not string.startswith("#")
        if not enabled:
            string = string[1:].lstrip()

        comments = None
        if "#" in string:
            comments = ["#".join(string.split("#")[1:])]
            string = string.split("#")[0]

        _, n, l, z_eff = string.split()
        return cls(
            n=int(n), l=l, z_eff=float(z_eff), enabled=enabled, comments=comments
        )

    def __str__(self) -> str:
        """Get the string representation for the control.in file."""
        return self.content_block(["z_eff"])


@dataclass(kw_only=True)
class IonicBasisFunction(BasisFunction):
    """The ionic basis function for FHI-aims.

    Parameters
    ----------
    radius: float
        The onset radius of the confining potential
        (in atomic units, 1 a.u.= 0.529177 Å). If the word auto is specified instead
        of a numerical value, the default onset radius given in the cut_pot
        tag is used.

    """

    radius: float | str
    type: str = "ionic"

    @classmethod
    def from_string(cls, string: str) -> IonicBasisFunction:
        """Get IonicBasisFunction object from string representation."""
        enabled = not string.startswith("#")
        if not enabled:
            string = string[1:].lstrip()

        comments = None
        if "#" in string:
            comments = ["#".join(string.split("#")[1:])]
            string = string.split("#")[0]

        _, n, l, radius = string.split()

        return cls(
            n=int(n),
            l=l,
            radius="auto" if radius == "auto" else float(radius),
            comments=comments,
            enabled=enabled,
        )

    def __str__(self) -> str:
        """Get the string representation for the control.in file."""
        return self.content_block(["radius"])


@dataclass(kw_only=True)
class ConfinedBasisFunction(BasisFunction):
    """The confined free-atom like radial basis function.

    Parameters
    ----------
    radius: float | str
        The onset radius of the confining potential
        (in atomic units, 1 a.u.= 0.529177 Å). If the word auto is specified instead
        of a numerical value, the default onset radius given in the cut_pot
        tag is used.

    """

    radius: float | str
    type: str = "confined"

    @classmethod
    def from_string(cls, string: str) -> ConfinedBasisFunction:
        """Get ConfinedBasisFunction object from string representation."""
        enabled = not string.startswith("#")
        if not enabled:
            string = string[1:].lstrip()

        comments = None
        if "#" in string:
            comments = ["#".join(string.split("#")[1:])]
            string = string.split("#")[0]

        _, n, l, radius = string.split()
        return cls(
            n=int(n),
            l=l,
            radius="auto" if radius == "auto" else float(radius),
            enabled=enabled,
            comments=comments,
        )

    def __str__(self) -> str:
        """Get the string representation for the control.in file."""
        return self.content_block(["radius"])


@dataclass(kw_only=True)
class STOBasisFunction(BasisFunction):
    """The STO basis function for FHI-aims.

    Parameters
    ----------
    zeta: float
        The STO exponent, which plays the role of the effective nuclear charge

    """

    zeta: float = field(default_factory=float)
    type: str = "sto"

    @classmethod
    def from_string(cls, string: str) -> STOBasisFunction:
        """Get ConfinedBasisFunction object from string representation."""
        enabled = not string.startswith("#")
        if not enabled:
            string = string[1:].lstrip()

        comments = None
        if "#" in string:
            comments = ["#".join(string.split("#")[1:])]
            string = string.split("#")

        _, n, l, zeta = string.split()
        l = int(l)
        return cls(n=int(n), l=l, zeta=float(zeta), enabled=enabled, comments=comments)

    def __str__(self) -> str:
        """Get the string representation for the control.in file."""
        return self.content_block(["zeta"])


@dataclass(kw_only=True)
class GaussianBasisFunction(BasisFunction):
    """The Gaussian basis function for FHI-aims.

    Parameters
    ----------
    n: int
        The number of Gaussian functions to comprise the basis function
    alpha_i: Sequence[float]
        The exponent defining a primitive Gaussian function [in bohr−2].
    coeff_i: Optional[Sequence[float]]
        The coefficients for the Gaussian functions if n > 1

    """

    alpha_i: Sequence[float]
    coeff_i: Sequence[float] | None
    type: str = "gaussian"

    def __post_init__(self):
        """Post init checks."""
        if self.n > 1 and not self.coeff_i:
            raise BasisFunctionError(
                f"Total number of Gaussians is {self.n} so coeff_i must be passed."
            )

        if len(self.alpha_i) != self.n:
            raise BasisFunctionError(f"The length of alpha_i must be {self.n}.")

        if self.coeff_i and (len(self.coeff_i) != self.n):
            raise BasisFunctionError(f"The length of coeff_i must be {self.n}.")

    @classmethod
    def from_string(cls, string: str) -> GaussianBasisFunction:
        """Get GaussianBasisFunction object from string representation."""
        alpha_i = []
        coeff_i = []
        lines = string.splitlines()

        comments = [
            "" if "#" not in line else "#".join(line.split("#")[1:]) for line in lines
        ]
        if all(comment == "" for comment in comments):
            comments = None

        _, l, *n = lines[0].split()
        if int(n[0]) == 1:
            alpha_i.append(float(n[1]))
        else:
            for line in lines[1:]:
                alpha_i.append(float(line.replace("#", "").split()[0]))
                coeff_i.append(float(line.replace("#", "").split()[1]))

        return cls(
            n=int(n[0]),
            l=l,
            alpha_i=alpha_i,
            coeff_i=coeff_i,
            comments=comments,
        )

    def __str__(self) -> str:
        """Get the content block for the control.in file."""
        title_line = (
            f"{'#' if not self.enabled else ''}"
            f"{'aux_' if self.aux else ''}{self.type:<11} "
            f"{self.l}  {self.n:6d}"
        )
        if self.n == 1:
            return f"{title_line}  {self.alpha_i[0]:.7f}"

        lines = [
            title_line,
        ]
        for alpha, coeff in zip(self.alpha_i, self.coeff_i, strict=False):
            lines.append(
                f"{'#' if not self.enabled else ' '}   {alpha:.7f}  {coeff:.7f}"
            )

        print("COMMENTS ", self.comments)
        if self.comments:
            lines = [
                f"{line} #{comment}" if comment != "" else line
                for line, comment in zip(lines, self.comments, strict=False)
            ]

        return "\n".join(lines)


BASIS_TYPES = {
    cls.type: cls
    for _, cls in inspect.getmembers(
        sys.modules[__name__],
        lambda member: inspect.isclass(member)
        and issubclass(member, BasisFunction)
        and member.__name__ != "BasisFunction",
    )
}
