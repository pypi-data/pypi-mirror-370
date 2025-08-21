from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_output_eospropertiestpn_ideal import ApiOutputEosPropertiesTPnResultIdeal
from ..models.api_output_eospropertiestpn_residual import ApiOutputEosPropertiesTPnResultResidual
from ..models.api_output_eospropertiestpn_sum import ApiOutputEosPropertiesTPnResultSum
from ..models.api_value_pressure import ApiValuePressure
from ..models.api_value_temperature import ApiValueTemperature
from ..models.api_value_volume import ApiValueVolume
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiOutputEosPropertiesTPnResult")


FIELD_MAP: Dict[str, str] = {
    "temperature": "temperature",
    "pressure": "pressure",
    "volume": "volume",
    "attractive_pressure": "attractivePressure",
    "repulsive_pressure": "repulsivePressure",
    "residual": "residual",
    "ideal": "ideal",
    "sum": "sum",
}

@attr.s(auto_attribs=True)
class ApiOutputEosPropertiesTPnResult:
    """Holds result for a point. This is stored in the `EosPropertiesTPnCalculationResult.point` attribute.
    
    Attributes
    ----------
    temperature : ApiValueTemperature
        Temperature of the phase.
    pressure : ApiValuePressure
        Pressure of the phase.
    volume : ApiValueVolume
        Volume of the phase.
    attractive_pressure : ApiValuePressure
        Attractive pressure of the phase.
    repulsive_pressure : ApiValuePressure
        Repulsive pressure of the phase.
    residual : ApiOutputEosPropertiesTPnResultResidual
        Residual thermodynamic properties of the phase.
    ideal : ApiOutputEosPropertiesTPnResultIdeal
        Ideal gas thermodynamic properties of the phase.
    sum : ApiOutputEosPropertiesTPnResultSum
        Sum (residual + ideal) of the thermodynamic properties of the phase.
    """
    temperature: Union[Unset, ApiValueTemperature] = UNSET
    pressure: Union[Unset, ApiValuePressure] = UNSET
    volume: Union[Unset, ApiValueVolume] = UNSET
    attractive_pressure: Union[Unset, ApiValuePressure] = UNSET
    repulsive_pressure: Union[Unset, ApiValuePressure] = UNSET
    residual: Union[Unset, ApiOutputEosPropertiesTPnResultResidual] = UNSET
    ideal: Union[Unset, ApiOutputEosPropertiesTPnResultIdeal] = UNSET
    sum: Union[Unset, ApiOutputEosPropertiesTPnResultSum] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiOutputEosPropertiesTPnResult` instance to a dict."""
        result: Dict[str, Any] = {}
        for attr_name, api_key in FIELD_MAP.items():
            val = getattr(self, attr_name)
            if isinstance(val, Unset):
                continue
            result[api_key] = val.to_dict() if hasattr(val, "to_dict") else val
        return result

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiOutputEosPropertiesTPnResult` instance from a dict."""
        d = src_dict.copy()
        kwargs = {}

        for field, api_key in FIELD_MAP.items():
            value = d.pop(api_key, UNSET)

            # custom deserialization for known nested models
            if field == "temperature" and not isinstance(value, Unset):
                value = ApiValueTemperature.from_dict(value)
            elif field == "pressure" and not isinstance(value, Unset):
                value = ApiValuePressure.from_dict(value)
            elif field == "volume" and not isinstance(value, Unset):
                value = ApiValueVolume.from_dict(value)
            elif field == "attractive_pressure" and not isinstance(value, Unset):
                value = ApiValuePressure.from_dict(value)
            elif field == "repulsive_pressure" and not isinstance(value, Unset):
                value = ApiValuePressure.from_dict(value)
            elif field == "residual" and not isinstance(value, Unset):
                value = ApiOutputEosPropertiesTPnResultResidual.from_dict(value)
            elif field == "ideal" and not isinstance(value, Unset):
                value = ApiOutputEosPropertiesTPnResultIdeal.from_dict(value)
            elif field == "sum" and not isinstance(value, Unset):
                value = ApiOutputEosPropertiesTPnResultSum.from_dict(value)
                
            kwargs[field] = value

        return cls(**kwargs)

    def __str__(self) -> str:
        """Formatted string representation of the `ApiOutputCalculationResultPhase` instance.
        Represents the properties using a table with columns: Property | Unit | Value.
        """
        def format_row(label: str, obj: Any) -> str:
            unit = getattr(obj, 'units', '-')
            value = getattr(obj, 'value', '-')

            if isinstance(value, float):
                value_str = f"{value:>15.8f}"
            else:
                value_str = f"{str(value):>15}"
            return f"{label:<25} | {unit:>15} | {value_str}"

        rows = ["TPn Result:"]
        rows.append(f"{'Property':<25} | {'Unit':>15} | {'Value':>15}")
        rows.append("-" * 62)

        rows.append(format_row("Temperature", self.temperature))
        rows.append(format_row("Pressure", self.pressure))
        rows.append(format_row("Volume", self.volume))
        rows.append(format_row("Attractive Pressure", self.attractive_pressure))
        rows.append(format_row("Repulsive Pressure", self.repulsive_pressure))

        if not isinstance(self.residual, Unset) and self.residual:
            rows.append("")
            rows.append("Residual Properties:")
            for attr_name in attr.fields_dict(type(self.residual)):
                val = getattr(self.residual, attr_name)
                rows.append(format_row(attr_name.replace("_", " ").title(), val))

        if not isinstance(self.ideal, Unset) and self.ideal:
            rows.append("")
            rows.append("Ideal Properties:")
            for attr_name in attr.fields_dict(type(self.ideal)):
                val = getattr(self.ideal, attr_name)
                rows.append(format_row(attr_name.replace("_", " ").title(), val))

        return "\n".join(rows)
