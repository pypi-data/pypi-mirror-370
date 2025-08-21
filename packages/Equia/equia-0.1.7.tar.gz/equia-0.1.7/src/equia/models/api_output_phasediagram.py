from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.api_output_phasediagram_point import ApiOutputPhasediagramPoint
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputPhasediagram")


@attr.s(auto_attribs=True)
class ApiOutputPhasediagram:
    """Result for a point.
    
    Attributes
    ----------
    temperature_units : str
        Units of the temperature.
    pressure_units : str
        Units of the pressure.
    phaseenvelope : List[ApiOutputPhasediagramPoint]
        Points of the phase envelope.
    vlle : List[ApiOutputPhasediagramPoint]
        Points of the VLLE curve.
    sle : List[ApiOutputPhasediagramPoint]
        Points of the SLE curve.
    spinodal : List[ApiOutputPhasediagramPoint]
        Points of the spinodal curve.
    slve : List[ApiOutputPhasediagramPoint]
        Points of the SLVE curve.
    """
    temperature_units: Union[Unset, None, str] = UNSET
    pressure_units: Union[Unset, None, str] = UNSET
    phaseenvelope: Union[Unset, None, List[ApiOutputPhasediagramPoint]] = UNSET
    vlle: Union[Unset, None, List[ApiOutputPhasediagramPoint]] = UNSET
    sle: Union[Unset, None, List[ApiOutputPhasediagramPoint]] = UNSET
    spinodal: Union[Unset, None, List[ApiOutputPhasediagramPoint]] = UNSET
    slve: Union[Unset, None, List[ApiOutputPhasediagramPoint]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputPhasediagram` instance to a dict."""
        temperature_units = self.temperature_units
        pressure_units = self.pressure_units
        phaseenvelope: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.phaseenvelope, Unset):
            if self.phaseenvelope is None:
                phaseenvelope = None
            else:
                phaseenvelope = []
                for phaseenvelope_item_data in self.phaseenvelope:
                    phaseenvelope_item = phaseenvelope_item_data.to_dict()

                    phaseenvelope.append(phaseenvelope_item)

        vlle: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.vlle, Unset):
            if self.vlle is None:
                vlle = None
            else:
                vlle = []
                for vlle_item_data in self.vlle:
                    vlle_item = vlle_item_data.to_dict()

                    vlle.append(vlle_item)

        sle: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sle, Unset):
            if self.sle is None:
                sle = None
            else:
                sle = []
                for sle_item_data in self.sle:
                    sle_item = sle_item_data.to_dict()

                    sle.append(sle_item)

        spinodal: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.spinodal, Unset):
            if self.spinodal is None:
                spinodal = None
            else:
                spinodal = []
                for spinodal_item_data in self.spinodal:
                    spinodal_item = spinodal_item_data.to_dict()

                    spinodal.append(spinodal_item)

        slve: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.slve, Unset):
            if self.slve is None:
                slve = None
            else:
                slve = []
                for slve_item_data in self.slve:
                    slve_item = slve_item_data.to_dict()

                    slve.append(slve_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if temperature_units is not UNSET:
            field_dict["temperatureUnits"] = temperature_units
        if pressure_units is not UNSET:
            field_dict["pressureUnits"] = pressure_units
        if phaseenvelope is not UNSET:
            field_dict["phaseenvelope"] = phaseenvelope
        if vlle is not UNSET:
            field_dict["vlle"] = vlle
        if sle is not UNSET:
            field_dict["sle"] = sle
        if spinodal is not UNSET:
            field_dict["spinodal"] = spinodal
        if slve is not UNSET:
            field_dict["slve"] = slve

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputPhasediagram` instance from a dict."""
        d = src_dict.copy()
        temperature_units = d.pop("temperatureUnits", UNSET)

        pressure_units = d.pop("pressureUnits", UNSET)

        phaseenvelope = []
        _phaseenvelope = d.pop("phaseenvelope", UNSET)
        for phaseenvelope_item_data in _phaseenvelope or []:
            phaseenvelope_item = ApiOutputPhasediagramPoint.from_dict(phaseenvelope_item_data)

            phaseenvelope.append(phaseenvelope_item)

        vlle = []
        _vlle = d.pop("vlle", UNSET)
        for vlle_item_data in _vlle or []:
            vlle_item = ApiOutputPhasediagramPoint.from_dict(vlle_item_data)

            vlle.append(vlle_item)

        sle = []
        _sle = d.pop("sle", UNSET)
        for sle_item_data in _sle or []:
            sle_item = ApiOutputPhasediagramPoint.from_dict(sle_item_data)

            sle.append(sle_item)

        spinodal = []
        _spinodal = d.pop("spinodal", UNSET)
        for spinodal_item_data in _spinodal or []:
            spinodal_item = ApiOutputPhasediagramPoint.from_dict(spinodal_item_data)

            spinodal.append(spinodal_item)

        slve = []
        _slve = d.pop("slve", UNSET)
        for slve_item_data in _slve or []:
            slve_item = ApiOutputPhasediagramPoint.from_dict(slve_item_data)

            slve.append(slve_item)

        api_output_phasediagram = cls(
            temperature_units=temperature_units,
            pressure_units=pressure_units,
            phaseenvelope=phaseenvelope,
            vlle=vlle,
            sle=sle,
            spinodal=spinodal,
            slve=slve,
        )

        return api_output_phasediagram
