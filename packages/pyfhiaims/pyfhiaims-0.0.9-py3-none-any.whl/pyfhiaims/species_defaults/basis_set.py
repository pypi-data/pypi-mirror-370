"""Definiton of the BasisSet objects for SpeciesDefinitions."""

from __future__ import annotations

from dataclasses import dataclass
from warnings import warn

from pyfhiaims.species_defaults.basis_function import BASIS_TYPES, BasisFunction
from pyfhiaims.utils import is_number_string


class TierNotFoundError(Exception):
    """Exception raised if requested tier does not exist."""


_TIERS = {
    "First tier": 1,
    "Second tier": 2,
    "Third tier": 3,
    "Fourth tier": 4,
    "Further basis functions": 5,
    "User added via pyaims.species_defaults.BasisSet": 6,
}


@dataclass
class BasisSet:
    """A basis set class for an FHI-aims species' defaults.

    Parameters
    ----------
    basis_set: list[list[BasisFunction]]

    """

    basis_set: list[list[BasisFunction]]

    def __str__(self):
        """Get the string for the basis set."""
        return self.to_string()

    @classmethod
    def from_string(cls, string: str) -> BasisSet:
        """Create a basis set instance from text block."""
        basis_set = [[]]
        lines = string.splitlines()
        tier = 1
        is_gaussian = False

        basis_lines = []
        for line in lines:
            line = line.strip()
            # check for the empty string
            if not line:
                continue
            # check for tier increase
            if line.startswith("#"):
                for k, tier_i in _TIERS.items():
                    if k in line:
                        tier = tier_i
                        if len(basis_set) < tier:
                            basis_set += [[] for _ in range(tier - len(basis_set))]
                        break
                # check if the commented line contains the disabled basis function
                words = line.replace("#", "").split()
                if len(words) < 1 or (
                    not any(bt in words[0] for bt in BASIS_TYPES)
                    and not is_number_string(line)
                ):
                    continue
            # gaussian is the only basis function that can span several lines
            if not is_gaussian:
                basis_lines.append(line)

            if not is_gaussian and "gaussian" in line:
                is_gaussian = True
                continue

            if is_gaussian and is_number_string(line):
                basis_lines.append(line)
                continue
            if is_gaussian:
                basis_set[tier - 1].append(
                    BasisFunction.from_string("\n".join(basis_lines))
                )
                is_gaussian = "gaussian" in line
                basis_lines = [line]

            if is_gaussian:
                continue
            basis_set[tier - 1].append(
                BasisFunction.from_string("\n".join(basis_lines))
            )
            basis_lines = []
        return cls(basis_set=basis_set)

    @property
    def n_tiers(self) -> int:
        """Returns the number of tiers in the set. Noise level functions always
        belong to Tier 5.
        """
        return len(self.basis_set)

    def tier(
        self, n: int, enabled: bool | None = None, aux: bool = False
    ) -> list[BasisFunction]:
        """Return all basis functions pertaining to the current tier.

        Parameters
        ----------
        n: int
            Ordinal number of the tier. First -> 1, Second -> 2, etc.
        enabled: bool | None
            A flag indicating whether only enabled or only disabled functions
            should be returned. If None, all functions are returned.
        aux: bool
            A flag indicating that aux functions should be returned.

        """
        if n < 1 or n > self.n_tiers:
            raise TierNotFoundError(
                f"No tier with ordinal value {n}. Tier value is [1, {self.n_tiers}]."
            )
        basis_tier = self.basis_set[n - 1]
        if enabled is None:
            return [f for f in basis_tier if f.aux == aux]

        return [f for f in basis_tier if (f.enabled == enabled and f.aux == aux)]

    def _switch_tier(
        self,
        tier: int,
        n: int | str = "all",
        aux: bool = False,
        enable: bool = True,
    ) -> None:
        """Swith the basis functions in the tier to on or off state.

        Parameters
        ----------
        tier: int
            Ordinal number of the tier you want to activate,
            First -> 1, Second -> 2, etc.
        n: int | str
            The number of functions you want to switch in that tier (`all` for entire)
        aux: bool
            the flag indicating if auxiliary functions should be switched.
        enable: bool
            A flag indicating in which state should the basis functions be.

        """
        if tier < 1 or tier > self.n_tiers:
            raise TierNotFoundError(
                f"No tier with ordinal value {tier}. Tier value is [1, {self.n_tiers}]."
            )

        if isinstance(n, int) and n > len(self.tier(tier, enabled=not enable, aux=aux)):
            warn(
                f"Requesting to {'de' if not enable else ''}activate "
                f"more functions in a tier than possible, just doing all.",
                RuntimeWarning,
                stacklevel=2,
            )
            n = "all"

        n = len(self.tier(tier, enabled=not enable, aux=aux)) if n == "all" else n
        i = 0
        for basis_function in self.basis_set[tier - 1][:: (-1) ** (not enable)]:
            if basis_function.enabled == (not enable) and basis_function.aux == aux:
                basis_function.enabled = enable
                i += 1
            if i == n:
                return

    def activate_tier(self, tier: int, n: int | str = "all", aux: bool = False) -> None:
        """Move basis functions in a specified tier from inactive to active.

        Parameters
        ----------
        tier: int
            Ordinal number of the tier you want to activate,
            First -> 1, Second -> 2, etc.
        n: int | str
            The number of functions you want to activate in that tier
            (all for entire)
        aux: bool
            the flag indicating if auxiliary functions should be activated.

        """
        self._switch_tier(tier, n, aux, enable=True)

    def deactivate_tier(
        self, tier: int, n: int | str = "all", aux: bool = False
    ) -> None:
        """Move basis functions in a specified tier from active to inactive.

        Parameters
        ----------
        tier: int
            Ordinal number of the tier you want to deactivate,
            First -> 1, Second -> 2, etc.
        n: int | str
            The number of functions you want to deactivate in that tier
            (all for entire)
        aux: bool
            the flag indicating if auxiliary functions should be activated.

        """
        self._switch_tier(tier, n, aux, enable=False)

    def _switch_functions(
        self, n: int | str = "all", aux: bool = False, enable: bool = True
    ) -> None:
        """Swith a basis functions (disregarding the tier) on or off.

        Parameters
        ----------
        n: int | str
            The number of functions you want to activate (all for entire basis_set)
        aux: bool
            the flag indicating if auxiliary functions should be switched.
        enable: bool
            A flag indicating in which state should the basis functions be.

        """
        valid_functions = sum(
            [len(self.tier(i + 1, not enable, aux)) for i in range(self.n_tiers)]
        )
        if isinstance(n, int) and n > valid_functions:
            warn(
                f"Requesting to {'de' if not enable else ''}activate "
                f"more functions than possible, just doing all.",
                RuntimeWarning,
                stacklevel=2,
            )
            n = "all"

        n = valid_functions if n == "all" else n
        if not enable:
            tier_list = list(range(self.n_tiers, 0, -1))
        else:
            tier_list = list(range(1, self.n_tiers + 1))
        for tier in tier_list:
            valid_fs_tier = len(self.tier(tier, not enable, aux))
            self._switch_tier(tier, min(n, valid_fs_tier), aux, enable)
            if valid_fs_tier < n:
                n -= valid_fs_tier
            else:
                return

    def activate_functions(self, n: int | str = "all", aux: bool = False) -> None:
        """Move basis functions from inactive to active.

        Parameters
        ----------
        n: int | str
            The number of functions you want to activate (all for entire basis_set)
        aux: bool
            the flag indicating if auxiliary functions should be activated.

        """
        self._switch_functions(n, aux, enable=True)

    def deactivate_functions(self, n: int | str = "all", aux: bool = False) -> None:
        """Move basis functions from active to inactive.

        Parameters
        ----------
        n: int | str
            The number of functions you want to activate (all for entire basis_set)
        aux: bool
            the flag indicating if auxiliary functions should be activated.

        """
        self._switch_functions(n, aux, enable=False)

    def add_function(
        self,
        basis_function: BasisFunction,
        tier: int | None = None,
        active: bool = True,
        aux: bool = False,
    ):
        """Add a basis function to a tier.

        Parameters
        ----------
        basis_function: BasisFunction
            The basis function to add
        tier: int
            The tier to add it to (if None, add to the last `User added` tier)
        active: bool
            If True then add the function to the active list
        aux: bool
            If True then add the function to the auxiliary basis set

        """
        if tier is not None and (tier < 1 or tier > self.n_tiers):
            raise TierNotFoundError(
                f"No tier with ordinal value {tier}. Tier value is [1, {self.n_tiers}]."
            )
        basis_function.enabled = active
        basis_function.aux = aux

        if tier is not None:
            self.basis_set[tier - 1].append(basis_function)
        else:
            user_tier = _TIERS["User added via pyaims.species_defaults.BasisSet"]
            if self.n_tiers < user_tier:
                self.basis_set += [[] for _ in range(user_tier - self.n_tiers)]
                self.basis_set[user_tier - 1].append(basis_function)

    def to_string(self):
        """Get the text block for the basis set."""
        comments_to_tiers = {v: k for k, v in _TIERS.items()}
        result = []
        for tier in range(1, self.n_tiers + 1):
            if self.basis_set[tier - 1]:
                result.append(f"#  {comments_to_tiers[tier]}")
                for basis_function in self.basis_set[tier - 1]:
                    result.append(str(basis_function))
        return "\n".join(result)
