from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.calculation_composition import CalculationComposition
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchFlashCalculationItem")

@attr.s(auto_attribs=True)
class BatchFlashCalculationItem:
    """Item for batch flash calculation.

    Attributes
    ----------
    components : List[CalculationComposition]
        Component composition
    temperature : float
        Temperature in units given in `BatchFlashCalculationInput.units` attribute.
    pressure : float
        Pressure in units given in `BatchFlashCalculationInput.units` attribute.
    enthalpy : float
        Enthalpy in units given in `BatchFlashCalculationInput.units` attribute.
    entropy : float
        Entropy in units given in `BatchFlashCalculationInput.units` attribute.
    """
    components: List[CalculationComposition] = UNSET # Component composition
    temperature: Union[Unset, float] = UNSET #Temperature in units given in 'Units' argument
    pressure: Union[Unset, float] = UNSET #Pressure in units given in 'Units' argument
    enthalpy: Union[Unset, float] = UNSET #Enthalpy in units given in 'Units' argument
    entropy: Union[Unset, float] = UNSET #Entropy in units given in 'Units' argument

    def to_dict(self) -> Dict[str, Any]:
        """Dump `BatchFlashCalculationItem` instance to a dict."""
        components = []
        for components_item_data in self.components:
            components_item = components_item_data.to_dict()
            components.append(components_item)

        temperature = self.temperature
        pressure = self.pressure
        enthalpy = self.enthalpy
        entropy = self.entropy

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "components": components,
            }
        )
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if pressure is not UNSET:
            field_dict["pressure"] = pressure
        if enthalpy is not UNSET:
            field_dict["enthalpy"] = enthalpy
        if entropy is not UNSET:
            field_dict["entropy"] = entropy

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `BatchFlashCalculationItem` instance from a dict."""
        d = src_dict.copy()

        components = []
        _components = d.pop("components")
        for components_item_data in _components:
            components_item = CalculationComposition.from_dict(
                components_item_data)

            components.append(components_item)

        temperature = d.pop("temperature", UNSET)
        pressure = d.pop("pressure", UNSET)
        enthalpy = d.pop("enthalpy", UNSET)
        entropy = d.pop("entropy", UNSET)

        flash_calculation_input = cls(
            components=components,
            temperature=temperature,
            pressure=pressure,
            enthalpy=enthalpy,
            entropy=entropy,
        )

        return flash_calculation_input
