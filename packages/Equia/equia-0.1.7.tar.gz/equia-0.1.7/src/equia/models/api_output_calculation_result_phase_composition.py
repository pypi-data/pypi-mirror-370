from typing import Any, Dict, Type, TypeVar, Union, List

import attr

from ..models.calculation_composition import CalculationComposition
from ..models.api_value_component_composition import ApiValueComponentComposition
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputCalculationResultPhaseComposition")


@attr.s(auto_attribs=True)
class ApiOutputCalculationResultPhaseComposition:
    """Holds composition information for a phase.
    
    Attributes
    ----------
    composition_units : str
        Units of the composition.
    molar_mass_units : str
        Units of the molar mass.
    components : List[ApiValueComponentComposition]
        Composition of the phase.
    """
    composition_units: Union[Unset, None, str] = UNSET
    molar_mass_units: Union[Unset, None, str] = UNSET
    components: Union[Unset, List[ApiValueComponentComposition]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputCalculationResultPhaseComposition` instance to a dict."""
        composition_units = self.composition_units
        molar_mass_units = self.molar_mass_units
        components: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.components, Unset):
            components = []
            for components_item_data in self.components:
                components.append(components_item_data.to_dict())

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if not isinstance(composition_units, Unset):
            field_dict["compositionUnits"] = composition_units
        if not isinstance(molar_mass_units, Unset):
            field_dict["molarMassUnits"] = molar_mass_units
        if not isinstance(components, Unset):
            field_dict["components"] = components

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputCalculationResultPhaseComposition` instance from a dict."""
        d = src_dict.copy()
        composition_units: str = d.pop("compositionUnits", UNSET)

        molar_mass_units: str = d.pop("molarMassUnits", UNSET)

        _components: List[Dict[str, Any]] = d.pop("components", UNSET)
        components: Union[Unset, List[ApiValueComponentComposition]]
        if isinstance(_components, Unset):
            components = UNSET
        else:
            components = []
            for components_item_data in _components:
                components.append(ApiValueComponentComposition.from_dict(components_item_data))

        api_output_calculation_result_phase_composition = cls(
            composition_units=composition_units,
            molar_mass_units=molar_mass_units,
            components=components,
        )

        return api_output_calculation_result_phase_composition

    def to_calculation_composition(self) -> List[CalculationComposition]:
        """
        Convert `ApiOutputCalculationResultPhaseComposition` to `List[CalculationComposition]`.
        
        Returns
        -------
        composition : List[CalculationComposition]
            Composition of the phase in format suitable for input to classes like `FlashCalculationInput.components`.
        """
        composition: List[CalculationComposition] = []
        for component in self.components:
            composition.append(
                CalculationComposition(
                    component_name=component.name,
                    amount=component.value,
                )
            )
        return composition

    def __str__(self) -> str:
        """
        Returns a string representation of the phase composition.
        """
        units = self.composition_units if not isinstance(self.composition_units, Unset) else "N/A"
        mm_units = self.molar_mass_units if not isinstance(self.molar_mass_units, Unset) else "N/A"
        lines = [f"Units: {units}, Molar Mass Units: {mm_units}"]

        if not isinstance(self.components, Unset) and self.components is not None:
            lines.append(str(self.components))
        else:
            lines.append("Composition: N/A")

        return "\n".join(lines)
