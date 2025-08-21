from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluidDistributionMoment")


@attr.s(auto_attribs=True)
class ApiFluidDistributionMoment:
    """Distribution for a fluid component

    Input is used to generate a distribution for the polymer

    One or more of Mn, Mw, Mz must be given"""

    model: Union[Unset, str] = UNSET
    number_of_pseudo_components: Union[Unset, int] = UNSET
    mn: Union[Unset, float] = UNSET
    mw: Union[Unset, float] = UNSET
    mz: Union[Unset, float] = UNSET
    minimum_molar_mass: Union[Unset, float] = UNSET
    maximum_molar_mass: Union[Unset, float] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluidDistributionMoment` instance to a dict."""
        model = self.model
        number_of_pseudo_components = self.number_of_pseudo_components
        mn = self.mn
        mw = self.mw
        mz = self.mz
        minimum_molar_mass = self.minimum_molar_mass
        maximum_molar_mass = self.maximum_molar_mass

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if model is not UNSET:
            field_dict["model"] = model
        if number_of_pseudo_components is not UNSET:
            field_dict["numberOfPseudoComponents"] = number_of_pseudo_components
        if mn is not UNSET:
            field_dict["mn"] = mn
        if mw is not UNSET:
            field_dict["mw"] = mw
        if mz is not UNSET:
            field_dict["mz"] = mz
        if minimum_molar_mass is not UNSET:
            field_dict["minimumMolarMass"] = minimum_molar_mass
        if maximum_molar_mass is not UNSET:
            field_dict["maximumMolarMass"] = maximum_molar_mass

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluidDistributionMoment` instance from a dict."""
        d = src_dict.copy()
        model = d.pop("model", UNSET)

        number_of_pseudo_components = d.pop("numberOfPseudoComponents", UNSET)

        mn = d.pop("mn", UNSET)

        mw = d.pop("mw", UNSET)

        mz = d.pop("mz", UNSET)

        minimum_molar_mass = d.pop("minimumMolarMass", UNSET)

        maximum_molar_mass = d.pop("maximumMolarMass", UNSET)

        api_fluid_distribution_moment = cls(
            model=model,
            number_of_pseudo_components=number_of_pseudo_components,
            mn=mn,
            mw=mw,
            mz=mz,
            minimum_molar_mass=minimum_molar_mass,
            maximum_molar_mass=maximum_molar_mass,
        )

        return api_fluid_distribution_moment
