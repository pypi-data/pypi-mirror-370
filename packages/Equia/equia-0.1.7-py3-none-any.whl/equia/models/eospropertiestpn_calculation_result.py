from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_output_eospropertiestpn_result import ApiOutputEosPropertiesTPnResult
from ..models.api_profile_information import ApiProfileInformation
from ..models.exception_info import ExceptionInfo
from ..types import UNSET, Unset
from ..str_util import default_result_str

T = TypeVar("T", bound="EosPropertiesTPnCalculationResult")


@attr.s(auto_attribs=True)
class EosPropertiesTPnCalculationResult:
    """Holds calculation result for a EoS TPn calculation.
    
    Attributes
    ----------
    success : bool
        Indicates if the calculation was successful.
    calculation_id : str
        Unique identifier for the calculation.
    exception_info : ExceptionInfo
        Information about any exceptions that occurred during the calculation.
    profiling : ApiProfileInformation
        Information about the profiling of the calculation.
    point : ApiOutputEosPropertiesTPnResult
        Calculation result for the point.
    """

    success: Union[Unset, bool] = UNSET
    calculation_id: Union[Unset, None, str] = UNSET
    exception_info: Union[Unset, ExceptionInfo] = UNSET
    profiling: Union[Unset, ApiProfileInformation] = UNSET
    point: Union[Unset, ApiOutputEosPropertiesTPnResult] = UNSET
    __str__ = default_result_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of this object."""
        success = self.success

        calculation_id = self.calculation_id
        exception_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exception_info, Unset):
            exception_info = self.exception_info.to_dict()

        profiling: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.profiling, Unset):
            profiling = self.profiling.to_dict()

        point: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.point, Unset):
            point = self.point.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if not isinstance(success, Unset):
            field_dict["success"] = success
        if not isinstance(calculation_id, Unset):
            field_dict["calculationId"] = calculation_id
        if not isinstance(exception_info, Unset):
            field_dict["exceptionInfo"] = exception_info
        if not isinstance(profiling, Unset):
            field_dict["profiling"] = profiling
        if not isinstance(point, Unset):
            field_dict["point"] = point

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of `EosPropertiesTPnCalculationResult` from a valid dictionary."""
        d = src_dict.copy()
        success = d.pop("success", UNSET)

        calculation_id = d.pop("calculationId", UNSET)

        _exception_info = d.pop("exceptionInfo", UNSET)
        exception_info: Union[Unset, ExceptionInfo]
        if isinstance(_exception_info, Unset):
            exception_info = UNSET
        else:
            exception_info = ExceptionInfo.from_dict(_exception_info)

        _profiling = d.pop("profiling", UNSET)
        profiling: Union[Unset, ApiProfileInformation]
        if isinstance(_profiling, Unset):
            profiling = UNSET
        else:
            profiling = ApiProfileInformation.from_dict(_profiling)

        _point = d.pop("point", UNSET)
        point: Union[Unset, ApiOutputEosPropertiesTPnResult]
        if isinstance(_point, Unset):
            point = UNSET
        else:
            point = ApiOutputEosPropertiesTPnResult.from_dict(_point)

        eospropertiestpn_calculation_result = cls(
            success=success,
            calculation_id=calculation_id,
            exception_info=exception_info,
            profiling=profiling,
            point=point,
        )

        return eospropertiestpn_calculation_result
