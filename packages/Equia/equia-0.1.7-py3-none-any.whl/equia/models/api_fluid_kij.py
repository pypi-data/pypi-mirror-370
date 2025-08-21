from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluidKij")


@attr.s(auto_attribs=True)
class ApiFluidKij:
    """
    Set of Kij information. To be used in the `ApiFluid.kij` attribute.
    
    Attributes
    ----------
    index_i : int
        Index of component i.
    index_j : int
        Index of component j.
    kija : float
        `kija` value for the expression `kij = kija + kijb * T(K)`.
    kijb : float
        `kijb` value for the expression `kij = kija + kijb * T(K)`.
    """
    index_i: Union[Unset, int] = UNSET
    index_j: Union[Unset, int] = UNSET
    kija: Union[Unset, float] = UNSET
    kijb: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluidKij` instance to a dict."""
        index_i = self.index_i
        index_j = self.index_j
        kija = self.kija
        kijb = self.kijb

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if not isinstance(index_i, Unset):
            field_dict["indexI"] = index_i
        if not isinstance(index_j, Unset):
            field_dict["indexJ"] = index_j
        if not isinstance(kija, Unset):
            field_dict["kija"] = kija
        if not isinstance(kijb, Unset):
            field_dict["kijb"] = kijb

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluidKij` instance from a dict."""
        d = src_dict.copy()
        index_i = d.pop("indexI", UNSET)

        index_j = d.pop("indexJ", UNSET)

        kija = d.pop("kija", UNSET)

        kijb = d.pop("kijb", UNSET)

        api_fluid_kij = cls(
            index_i=index_i,
            index_j=index_j,
            kija=kija,
            kijb=kijb,
        )

        return api_fluid_kij

    def __str__(self) -> str:
        """
        Returns a string representation in the form: Kij(i, j) = (kija, kijb)
        """
        i = self.index_i if not isinstance(self.index_i, Unset) else "?"
        j = self.index_j if not isinstance(self.index_j, Unset) else "?"
        a = self.kija if not isinstance(self.kija, Unset) else "?"
        b = self.kijb if not isinstance(self.kijb, Unset) else 0
        return f"Kij({i}, {j}) = ({a}, {b})"
