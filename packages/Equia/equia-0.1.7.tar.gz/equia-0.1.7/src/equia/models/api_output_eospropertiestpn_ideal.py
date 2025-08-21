from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_value_floating_with_units import ApiValueFloatingWithUnits
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputEosPropertiesTPnResultIdeal")


@attr.s(auto_attribs=True)
class ApiOutputEosPropertiesTPnResultIdeal:
    """Holds ideal values. This is stored in the `ApiOutputEosPropertiesTPnResult.ideal` attribute.
    
    Attributes
    ----------
    volume : ApiValueFloatingWithUnits
        Volume of the phase.
    gibbs_energy : ApiValueFloatingWithUnits
        Gibbs energy of the phase.
    internal_energy : ApiValueFloatingWithUnits
        Internal energy of the phase.
    helmholtz_energy : ApiValueFloatingWithUnits
        Helmholtz energy of the phase.
    cv : ApiValueFloatingWithUnits
        Specific heat capacity of the phase.
    cp : ApiValueFloatingWithUnits
        Specific heat capacity of the phase.
    enthalpy : ApiValueFloatingWithUnits
        Enthalpy of the phase.
    entropy : ApiValueFloatingWithUnits
        Entropy of the phase.
    """

    volume: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    gibbs_energy: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    internal_energy: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    helmholtz_energy: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    cv: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    cp: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    enthalpy: Union[Unset, ApiValueFloatingWithUnits] = UNSET
    entropy: Union[Unset, ApiValueFloatingWithUnits] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputEosPropertiesTPnResultIdeal` instance to a dict."""
        volume: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.volume, Unset):
            volume = self.volume.to_dict()

        gibbs_energy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.gibbs_energy, Unset):
            gibbs_energy = self.gibbs_energy.to_dict()

        internal_energy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.internal_energy, Unset):
            internal_energy = self.internal_energy.to_dict()

        helmholtz_energy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.helmholtz_energy, Unset):
            helmholtz_energy = self.helmholtz_energy.to_dict()

        cv: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cv, Unset):
            cv = self.cv.to_dict()

        cp: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.cp, Unset):
            cp = self.cp.to_dict()

        enthalpy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.enthalpy, Unset):
            enthalpy = self.enthalpy.to_dict()

        entropy: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.entropy, Unset):
            entropy = self.entropy.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if volume is not UNSET:
            field_dict["volume"] = volume
        if gibbs_energy is not UNSET:
            field_dict["gibbsEnergy"] = gibbs_energy
        if internal_energy is not UNSET:
            field_dict["internalEnergy"] = internal_energy
        if helmholtz_energy is not UNSET:
            field_dict["helmholtzEnergy"] = helmholtz_energy
        if cv is not UNSET:
            field_dict["cv"] = cv
        if cp is not UNSET:
            field_dict["cp"] = cp
        if enthalpy is not UNSET:
            field_dict["enthalpy"] = enthalpy
        if entropy is not UNSET:
            field_dict["entropy"] = entropy

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputEosPropertiesTPnResultIdeal` instance from a dict."""
        d = src_dict.copy()
        _volume = d.pop("volume", UNSET)
        volume: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_volume, Unset):
            volume = UNSET
        else:
            volume = ApiValueFloatingWithUnits.from_dict(_volume)

        _gibbs_energy = d.pop("gibbsEnergy", UNSET)
        gibbs_energy: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_gibbs_energy, Unset):
            gibbs_energy = UNSET
        else:
            gibbs_energy = ApiValueFloatingWithUnits.from_dict(_gibbs_energy)

        _internal_energy = d.pop("internalEnergy", UNSET)
        internal_energy: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_internal_energy, Unset):
            internal_energy = UNSET
        else:
            internal_energy = ApiValueFloatingWithUnits.from_dict(_internal_energy)

        _helmholtz_energy = d.pop("helmholtzEnergy", UNSET)
        helmholtz_energy: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_helmholtz_energy, Unset):
            helmholtz_energy = UNSET
        else:
            helmholtz_energy = ApiValueFloatingWithUnits.from_dict(_helmholtz_energy)

        _cv = d.pop("cv", UNSET)
        cv: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_cv, Unset):
            cv = UNSET
        else:
            cv = ApiValueFloatingWithUnits.from_dict(_cv)

        _cp = d.pop("cp", UNSET)
        cp: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_cp, Unset):
            cp = UNSET
        else:
            cp = ApiValueFloatingWithUnits.from_dict(_cp)

        _enthalpy = d.pop("enthalpy", UNSET)
        enthalpy: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_enthalpy, Unset):
            enthalpy = UNSET
        else:
            enthalpy = ApiValueFloatingWithUnits.from_dict(_enthalpy)

        _entropy = d.pop("entropy", UNSET)
        entropy: Union[Unset, ApiValueFloatingWithUnits]
        if isinstance(_entropy, Unset):
            entropy = UNSET
        else:
            entropy = ApiValueFloatingWithUnits.from_dict(_entropy)

        api_output_eospropertiestpn_ideal = cls(
            volume=volume,
            gibbs_energy=gibbs_energy,
            internal_energy=internal_energy,
            helmholtz_energy=helmholtz_energy,
            cv=cv,
            cp=cp,
            enthalpy=enthalpy,
            entropy=entropy,
        )

        return api_output_eospropertiestpn_ideal

    def __str__(self) -> str:
        """
        Returns a compact string of non-Unset ideal gas properties.
        """
        items = []
        for field in self.__annotations__:
            val = getattr(self, field)
            if not isinstance(val, Unset):
                items.append(f"{field}={val}")
        return ", ".join(items)
