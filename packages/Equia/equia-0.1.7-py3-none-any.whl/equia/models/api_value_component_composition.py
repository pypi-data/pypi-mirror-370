from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.api_value_floating_with_out_units_name import ApiValueFloatingWithOutUnitsName
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiValueComponentComposition")


@attr.s(auto_attribs=True)
class ApiValueComponentComposition:
    """Holds composition info.

    Attributes
    ----------
    name : str
        Name of the component.
    value : float
        Value of the component.
    distribution : List[ApiValueFloatingWithOutUnitsName]
        Distribution of the component.
    """
    name: Union[Unset, None, str] = UNSET
    value: Union[Unset, float] = UNSET
    distribution: Union[Unset, None, List[ApiValueFloatingWithOutUnitsName]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiValueComponentComposition` instance to a dict."""
        name = self.name
        value = self.value
        distribution: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.distribution, Unset):
            if self.distribution is None:
                distribution = None
            else:
                distribution = []
                for distribution_item_data in self.distribution:
                    distribution_item = distribution_item_data.to_dict()

                    distribution.append(distribution_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if value is not UNSET:
            field_dict["value"] = value
        if distribution is not UNSET:
            field_dict["distribution"] = distribution

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiValueComponentComposition` instance from a dict."""
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        value = d.pop("value", UNSET)

        distribution = []
        _distribution = d.pop("distribution", UNSET)
        for distribution_item_data in _distribution or []:
            distribution_item = ApiValueFloatingWithOutUnitsName.from_dict(distribution_item_data)

            distribution.append(distribution_item)

        api_value_component_composition = cls(
            name=name,
            value=value,
            distribution=distribution,
        )

        return api_value_component_composition
