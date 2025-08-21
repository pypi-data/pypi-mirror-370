from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueFloatingWithOutUnitsName")


@attr.s(auto_attribs=True)
class ApiValueFloatingWithOutUnitsName:
    """Holds composition value.

    Attributes
    ----------
    value : float
        Value of the component.
    name : str
        Name of the component.
    molar_mass : float
        Molar mass of the component.
    """
    value: Union[Unset, float] = UNSET
    name: Union[Unset, None, str] = UNSET
    molar_mass: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiValueFloatingWithOutUnitsName` instance to a dict."""
        value = self.value
        name = self.name
        molar_mass = self.molar_mass

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if name is not UNSET:
            field_dict["name"] = name
        if molar_mass is not UNSET:
            field_dict["molarMass"] = molar_mass

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiValueFloatingWithOutUnitsName` instance from a dict."""
        d = src_dict.copy()
        value = d.pop("value", UNSET)

        name = d.pop("name", UNSET)

        molar_mass = d.pop("molarMass", UNSET)

        api_value_floating_with_out_units_name = cls(
            value=value,
            name=name,
            molar_mass=molar_mass,
        )

        return api_value_floating_with_out_units_name
