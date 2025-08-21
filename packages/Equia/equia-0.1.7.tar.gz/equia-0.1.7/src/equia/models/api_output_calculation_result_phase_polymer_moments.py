from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.api_output_calculation_result_phase_polymer_moment import ApiOutputCalculationResultPhasePolymerMoment
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputCalculationResultPhasePolymerMoments")


@attr.s(auto_attribs=True)
class ApiOutputCalculationResultPhasePolymerMoments:
    """Polymer moments.

    Attributes
    ----------
    moment_units : str
        Units of the moments.
    polymers : List[ApiOutputCalculationResultPhasePolymerMoment]
        List of polymer moments.
    """
    moment_units: Union[Unset, None, str] = UNSET
    polymers: Union[Unset, None, List[ApiOutputCalculationResultPhasePolymerMoment]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputCalculationResultPhasePolymerMoments` instance to a dict."""
        moment_units = self.moment_units
        polymers: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.polymers, Unset):
            if self.polymers is None:
                polymers = None
            else:
                polymers = []
                for polymers_item_data in self.polymers:
                    polymers_item = polymers_item_data.to_dict()

                    polymers.append(polymers_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if moment_units is not UNSET:
            field_dict["momentUnits"] = moment_units
        if polymers is not UNSET:
            field_dict["polymers"] = polymers

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputCalculationResultPhasePolymerMoments` instance from a dict."""
        d = src_dict.copy()
        moment_units = d.pop("momentUnits", UNSET)

        polymers = []
        _polymers = d.pop("polymers", UNSET)
        for polymers_item_data in _polymers or []:
            polymers_item = ApiOutputCalculationResultPhasePolymerMoment.from_dict(polymers_item_data)

            polymers.append(polymers_item)

        api_output_calculation_result_phase_polymer_moments = cls(
            moment_units=moment_units,
            polymers=polymers,
        )

        return api_output_calculation_result_phase_polymer_moments
