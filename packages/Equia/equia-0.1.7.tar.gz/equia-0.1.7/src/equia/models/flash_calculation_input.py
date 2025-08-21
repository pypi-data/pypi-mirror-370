"""
Module for representing a flash calculation input.
"""
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.calculation_composition import CalculationComposition
from ..models.api_fluid import ApiFluid
from ..types import UNSET, Unset
from ..str_util import default_input_str
from ..options import FlashType

T = TypeVar("T", bound="FlashCalculationInput")


@attr.s(auto_attribs=True)
class FlashCalculationInput:
    """Input for flash calculation.

    Attributes
    ----------
    access_key : str
        Access key for the API.
    components : List[CalculationComposition]
        Component composition
    flashtype : str 
        Type of flash to perform. 
        Allowed options: `{'FixedTemperaturePressure', 'FixedPressureEnthalpy', 'FixedPressureEntropy', 'FixedTemperatureVolume'}`
    units : str 
        Units used for input and output.
    fluidid : str 
        Id of fluid on webserver. Must be defined if `fluid` argument is not given.
    fluid : ApiFluid
        Fluid information
    temperature : float
        Temperature in units given in `units` argument.
    pressure : float
        Pressure in units given in `units` argument.
    enthalpy : float
        Enthalpy in units given in `units` argument.
    entropy : float
        Entropy in units given in `units` argument.
    """
    access_key: str
    components: List[CalculationComposition]
    flashtype: str = attr.ib(converter=FlashType.to_str)
    units: str
    fluidid: Union[Unset, str] = UNSET
    fluid: Union[Unset, ApiFluid] = UNSET
    temperature: Union[Unset, float] = UNSET
    pressure: Union[Unset, float] = UNSET
    enthalpy: Union[Unset, float] = UNSET
    entropy: Union[Unset, float] = UNSET
    __str__ = default_input_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Dump `FlashCalculationInput` instance to a dict."""
        access_key = self.access_key
        components = []
        for components_item_data in self.components:
            components_item = components_item_data.to_dict()
            components.append(components_item)

        flashtype = FlashType(self.flashtype).value
        units = self.units
        temperature = self.temperature
        pressure = self.pressure
        enthalpy = self.enthalpy
        entropy = self.entropy

        fluidid: Union[Unset, str] = UNSET
        if not isinstance(self.fluidid, Unset):
            fluid = self.fluidid

        fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fluid, Unset):
            fluid = self.fluid.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessKey": access_key,
                "components": components,
                "flashType": flashtype,
            }
        )
        if not isinstance(units, Unset):
            field_dict["units"] = units
        if not isinstance(fluidid, Unset):
            field_dict["fluidId"] = fluidid
        if not isinstance(fluid, Unset):
            field_dict["fluid"] = fluid
        if not isinstance(temperature, Unset):
            field_dict["temperature"] = temperature
        if not isinstance(pressure, Unset):
            field_dict["pressure"] = pressure
        if not isinstance(enthalpy, Unset):
            field_dict["enthalpy"] = enthalpy
        if not isinstance(entropy, Unset):
            field_dict["entropy"] = entropy

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `FlashCalculationInput` instance from a dict."""
        d = src_dict.copy()
        access_key = d.pop("accessKey")
        flashtype = FlashType(d.pop("flashType", FlashType.FixedTemperaturePressure.value)).value
        units = d.pop("units", UNSET)

        components = []
        _components = d.pop("components")
        for components_item_data in _components:
            components_item = CalculationComposition.from_dict(
                components_item_data)

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

        temperature = d.pop("temperature", UNSET)
        pressure = d.pop("pressure", UNSET)
        enthalpy = d.pop("enthalpy", UNSET)
        entropy = d.pop("entropy", UNSET)

        flash_calculation_input = cls(
            access_key=access_key,
            components=components,
            flashtype=flashtype,
            units=units,
            fluidid=fluidid,
            fluid=fluid,
            temperature=temperature,
            pressure=pressure,
            enthalpy=enthalpy,
            entropy=entropy,
        )

        return flash_calculation_input

    @classmethod
    def from_input_object(cls: Type[T], input_object: "FlashCalculationInput") -> T:
        """Load `FlashCalculationInput` instance from a similar instance, such as `FlashCalculationInput`.
        This is useful for copying data from one instance to another.
        
        Parameters
        ----------
        input_object : Union[EosPropertiesTPnCalculationInput, FlashCalculationInput, CloudPointCalculationInput]
            Instance to copy data from.
        
        Returns
        -------
        FlashCalculationInput
            New instance with copied data.
        """
        d = input_object.to_dict()
        return cls.from_dict(d)
