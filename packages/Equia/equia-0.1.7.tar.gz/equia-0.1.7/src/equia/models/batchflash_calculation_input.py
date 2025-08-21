from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.batchflash_calculation_item import BatchFlashCalculationItem
from ..models.api_fluid import ApiFluid
from ..types import UNSET, Unset
from ..options import FlashType

T = TypeVar("T", bound="BatchFlashCalculationInput")

@attr.s(auto_attribs=True)
class BatchFlashCalculationInput:
    """Input for batch flash calculation.
    
    Attributes
    ----------
    access_key : str
        Access key for the API. This is used to authenticate the user.
    flashtype : str
        Type of flash to perform. 
        Allowed options: `{'FixedTemperaturePressure', 'FixedPressureEnthalpy', 'FixedPressureEntropy', 'FixedTemperatureVolume'}`
    units : str
        Units used for input and output.
    points : List[BatchFlashCalculationItem]
        Flash points.
    fluidid : str, optional
        Id of fluid on webserver. Must be defined if no fluid given in fluid argument
    fluid : ApiFluid
        Fluid information
    """
    access_key: str
    flashtype: str = attr.ib(converter=FlashType.to_str)
    units: str
    points: List[BatchFlashCalculationItem]
    fluidid: Union[Unset, str] = UNSET
    fluid: Union[Unset, ApiFluid] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `BatchFlashCalculationInput` instance to a dict."""
        access_key = self.access_key
        points = []
        for item_data in self.points:
            item = item_data.to_dict()
            points.append(item)

        flashtype = FlashType(self.flashtype).value
        units = self.units

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
                "points": points,
                "flashType": flashtype,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units
        if fluidid is not UNSET:
            field_dict["fluidId"] = fluidid
        if fluid is not UNSET:
            field_dict["fluid"] = fluid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `BatchFlashCalculationInput` instance from a dict."""
        d = src_dict.copy()
        access_key = d.pop("accessKey")
        flashtype = FlashType(d.pop("flashType", FlashType.FixedTemperaturePressure.value)).value
        units = d.pop("units", UNSET)

        points = []
        _points = d.pop("points")
        for item_data in _points:
            item = BatchFlashCalculationItem.from_dict(item_data)
            points.append(item)

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

        batchflash_calculation_input = cls(
            access_key=access_key,
            points=points,
            flashtype=flashtype,
            units=units,
            fluidid=fluidid,
            fluid=fluid,
        )

        return batchflash_calculation_input

    @classmethod
    def from_input_object(cls: Type[T], input_object: "BatchFlashCalculationInput") -> T:
        """Load `BatchFlashCalculationInput` instance from a similar instance, such as `FlashCalculationInput`.
        This is useful for copying data from one instance to another.
        
        Parameters
        ----------
        input_object : Union[EosPropertiesTPnCalculationInput, FlashCalculationInput, CloudPointCalculationInput, BatchFlashCalculationInput]
            Instance to copy data from.
        
        Returns
        -------
        EosPropertiesTPnCalculationInput
            New instance with copied data.
        """
        d = input_object.to_dict()
        return cls.from_dict(d)
