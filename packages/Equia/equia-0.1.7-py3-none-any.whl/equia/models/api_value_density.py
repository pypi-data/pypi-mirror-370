from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueDensity")


@attr.s(auto_attribs=True)
class ApiValueDensity:
    """Holds density information.

    Attributes
    ----------
    units : str
        Units.
    value : float
        Value.
    """

    units: Union[Unset, None, str] = UNSET
    value: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiValueDensity` instance to a dict."""
        units = self.units
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if units is not UNSET:
            field_dict["units"] = units
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiValueDensity` instance from a dict."""
        d = src_dict.copy()
        units = d.pop("units", UNSET)

        value = d.pop("value", UNSET)

        api_value_density = cls(
            units=units,
            value=value,
        )

        return api_value_density
