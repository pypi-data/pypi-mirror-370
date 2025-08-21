from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputPhasediagramPoint")


@attr.s(auto_attribs=True)
class ApiOutputPhasediagramPoint:
    """Result for a point.

    Attributes
    ----------
    temperature : float
        Temperature of the point.
    pressure : float
        Pressure of the point.
    label : str
        Label of the point.
    """
    temperature: Union[Unset, float] = UNSET
    pressure: Union[Unset, float] = UNSET
    label: Union[Unset, None, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputPhasediagramPoint` instance to a dict."""
        temperature = self.temperature
        pressure = self.pressure
        label = self.label

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if pressure is not UNSET:
            field_dict["pressure"] = pressure
        if label is not UNSET:
            field_dict["label"] = label

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputPhasediagramPoint` instance from a dict."""
        d = src_dict.copy()
        temperature = d.pop("temperature", UNSET)

        pressure = d.pop("pressure", UNSET)

        label = d.pop("label", UNSET)

        api_output_phasediagram_point = cls(
            temperature=temperature,
            pressure=pressure,
            label=label,
        )

        return api_output_phasediagram_point
