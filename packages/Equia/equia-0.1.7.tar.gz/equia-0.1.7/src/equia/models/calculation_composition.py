"""
Module for representing a component composition of a fluid mixture.

This class is intended to serialize/deserialize data in a format compatible with the VLXE API.
"""
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="CalculationComposition")


@attr.s(auto_attribs=True)
class CalculationComposition:
    """Holds composition information for a component.
    
    This information to be stored in the `components: List[CalculationComposition]` attribute of input classes such as `FlashCalculationInput` or `EosPropertiesTPnCalculationInput`.
    
    Attributes
    ----------
    component_id : str
        Id of the component.
    component_name : str
        Name of the component.
    amount : float
        Amount of the component (in units defined in the `units` attribute).
    """
    component_id: Union[Unset, str] = UNSET
    component_name: Union[Unset, None, str] = UNSET
    amount: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `CalculationComposition` instance to a dict."""
        component_id = self.component_id
        component_name = self.component_name
        amount = self.amount

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if not isinstance(component_id, Unset):
            field_dict["componentId"] = component_id
        if not isinstance(component_name, Unset):
            field_dict["componentName"] = component_name
        if not isinstance(amount, Unset):
            field_dict["amount"] = amount

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `CalculationComposition` instance from a dict."""
        d = src_dict.copy()
        component_id = d.pop("componentId", UNSET)

        component_name = d.pop("componentName", UNSET)

        amount = d.pop("amount", UNSET)

        calculation_composition = cls(
            component_id=component_id,
            component_name=component_name,
            amount=amount,
        )

        return calculation_composition

    def __str__(self) -> str:
        """
        Returns a string representation of the `CalculationComposition` instance.
        
        Includes:
        - Component name, ID, and amount.
        """
        parts = []
        name = self.component_name if not isinstance(self.component_name, Unset) else "N/A"
        comp_id = self.component_id if not isinstance(self.component_id, Unset) else "N/A"
        amount = self.amount if not isinstance(self.amount, Unset) else "N/A"
        
        parts.append(f"Component: {name} (ID: {comp_id})")
        parts.append(f"  Amount: {amount}")

        return "\n".join(parts)
