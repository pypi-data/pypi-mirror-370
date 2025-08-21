from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputCalculationResultPhasePolymerMoment")


@attr.s(auto_attribs=True)
class ApiOutputCalculationResultPhasePolymerMoment:
    """Moment for a polymer in a phase.
    
    Attributes
    ----------
    polymer_name : str
        Name of the polymer.
    mn : float
        Number-average molecular weight of the polymer.
    mw : float
        Weight-average molecular weight of the polymer.
    mz : float
        z-average molecular weight of the polymer.
    """
    polymer_name: Union[Unset, None, str] = UNSET
    mn: Union[Unset, float] = UNSET
    mw: Union[Unset, float] = UNSET
    mz: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputCalculationResultPhasePolymerMoment` instance to a dict."""
        polymer_name = self.polymer_name
        mn = self.mn
        mw = self.mw
        mz = self.mz

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if polymer_name is not UNSET:
            field_dict["polymerName"] = polymer_name
        if mn is not UNSET:
            field_dict["mn"] = mn
        if mw is not UNSET:
            field_dict["mw"] = mw
        if mz is not UNSET:
            field_dict["mz"] = mz

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputCalculationResultPhasePolymerMoment` instance from a dict."""
        d = src_dict.copy()
        polymer_name = d.pop("polymerName", UNSET)

        mn = d.pop("mn", UNSET)

        mw = d.pop("mw", UNSET)

        mz = d.pop("mz", UNSET)

        api_output_calculation_result_phase_polymer_moment = cls(
            polymer_name=polymer_name,
            mn=mn,
            mw=mw,
            mz=mz,
        )

        return api_output_calculation_result_phase_polymer_moment
