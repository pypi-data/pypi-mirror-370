from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.calculation_composition import CalculationComposition
from ..models.api_fluid import ApiFluid
from ..types import UNSET, Unset

T = TypeVar("T", bound="PhasediagramFixedTemperaturePressureCalculationInput")


@attr.s(auto_attribs=True)
class PhasediagramFixedTemperaturePressureCalculationInput:
    """Input to phase diagram calculation at fixed temperature/pressure.
    
    Attributes
    ----------
    access_key : str
        Access key for the API. This is used to authenticate the user.
    components : List[CalculationComposition]
        List of components in the mixture.
    units : str
        Units for the calculation.
    fluidid : str
        Id of fluid on webserver. Must be defined if no fluid given in fluid argument
    fluid : ApiFluid
        Fluid information
    vlle : bool
        Calculate VLLE curve.
    sle : bool
        Calculate SLE curve.
    slve : bool
        Calculate SLVE curve.
    spinodal : bool
        Calculate spinodal curve.
    """
    access_key: str
    components: List[CalculationComposition]
    units: str
    fluidid: Union[Unset, str] = UNSET #Id of fluid on webserver. Must be defined if no fluid given in fluid argument
    fluid: Union[Unset, ApiFluid] = UNSET #Fluid information
    vlle: Union[Unset, bool] = UNSET
    sle: Union[Unset, bool] = UNSET
    slve: Union[Unset, bool] = UNSET
    spinodal: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `PhasediagramFixedTemperaturePressureCalculationInput` instance to a dict."""
        access_key = self.access_key
        components = []
        for components_item_data in self.components:
            components_item = components_item_data.to_dict()

            components.append(components_item)

        fluidid: Union[Unset, str] = UNSET
        if not isinstance(self.fluidid, Unset):
            fluid = self.fluidid

        fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fluid, Unset):
            fluid = self.fluid.to_dict()        

        units = self.units

        vlle = self.vlle
        sle = self.sle
        slve = self.slve
        spinodal = self.spinodal

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessKey": access_key,
                "components": components,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units
        if fluidid is not UNSET:
            field_dict["fluidId"] = fluidid
        if fluid is not UNSET:
            field_dict["fluid"] = fluid
        if vlle is not UNSET:
            field_dict["vlle"] = vlle
        if sle is not UNSET:
            field_dict["sle"] = sle
        if slve is not UNSET:
            field_dict["slve"] = slve
        if spinodal is not UNSET:
            field_dict["spinodal"] = spinodal

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `PhasediagramFixedTemperaturePressureCalculationInput` instance from a dict."""
        d = src_dict.copy()

        access_key = d.pop("accessKey")

        components = []
        _components = d.pop("components")
        for components_item_data in _components:
            components_item = CalculationComposition.from_dict(components_item_data)

            components.append(components_item)

        _fluidid = d.pop("fluidId", UNSET)
        fluidid: Union[Unset, str]
        if isinstance(_fluidid, Unset):
            fluidid = UNSET
        else:
            fluidid = _fluidid

        _fluid = d.pop("fluid", UNSET)
        fluid: Union[Unset, ApiFluid]
        if isinstance(_fluid, Unset):
            fluid = UNSET
        else:
            fluid = ApiFluid.from_dict(_fluid)

        units = d.pop("units", UNSET)

        vlle = d.pop("vlle", UNSET)

        sle = d.pop("sle", UNSET)

        slve = d.pop("slve", UNSET)

        spinodal = d.pop("spinodal", UNSET)

        phasediagram_fixed_temperature_pressure_calculation_input = cls(
            access_key=access_key,
            components=components,
            fluidid=fluidid,
            fluid=fluid,
            units=units,
            vlle=vlle,
            sle=sle,
            slve=slve,
            spinodal=spinodal,
        )

        return phasediagram_fixed_temperature_pressure_calculation_input
