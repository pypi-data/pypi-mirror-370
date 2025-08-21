from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueFloatingWithUnits")


@attr.s(auto_attribs=True)
class ApiValueFloatingWithUnits:
    """Holds floating value with units"""

    units: Union[Unset, None, str] = UNSET
    value: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
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
        d = src_dict.copy()
        units = d.pop("units", UNSET)

        value = d.pop("value", UNSET)

        api_value_floating_with_units = cls(
            units=units,
            value=value,
        )

        return api_value_floating_with_units
