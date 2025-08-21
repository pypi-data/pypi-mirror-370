from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueFloatingWithOutUnits")


@attr.s(auto_attribs=True)
class ApiValueFloatingWithOutUnits:
    """Value with out any units given.

    Attributes
    ----------
    value : float
        Value of the property.
    """
    value: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiValueFloatingWithOutUnits` instance to a dict."""
        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiValueFloatingWithOutUnits` instance from a dict."""
        d = src_dict.copy()
        value = d.pop("value", UNSET)

        api_value_floating_with_out_units = cls(
            value=value,
        )

        return api_value_floating_with_out_units
