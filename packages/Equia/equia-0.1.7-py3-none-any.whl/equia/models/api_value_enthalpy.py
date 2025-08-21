from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueEnthalpy")


@attr.s(auto_attribs=True)
class ApiValueEnthalpy:
    """Holds enthalpy information.
    
    Attributes
    ----------
    units : str
        Enthalpy units.
    value : float
        Enthalpy value.
    """
    units: Union[Unset, None, str] = UNSET
    value: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiValueEnthalpy` instance to a dict."""
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
        """Load `ApiValueEnthalpy` instance from a dict."""
        d = src_dict.copy()
        units = d.pop("units", UNSET)

        value = d.pop("value", UNSET)

        api_value_enthalpy = cls(
            units=units,
            value=value,
        )

        return api_value_enthalpy
