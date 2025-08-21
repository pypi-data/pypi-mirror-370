from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_output_calculation_result_point import ApiOutputCalculationResultPoint
from ..models.api_profile_information import ApiProfileInformation
from ..models.exception_info import ExceptionInfo
from ..types import UNSET, Unset
from ..str_util import default_result_str

T = TypeVar("T", bound="CloudPointCalculationResult")


@attr.s(auto_attribs=True)
class CloudPointCalculationResult:
    """Holds calculation result for a point.
    
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
    point : ApiOutputCalculationResultPoint
        Calculation result for the point.
    """
    success: Union[Unset, bool] = UNSET
    calculation_id: Union[Unset, None, str] = UNSET
    exception_info: Union[Unset, ExceptionInfo] = UNSET
    profiling: Union[Unset, ApiProfileInformation] = UNSET
    point: Union[Unset, ApiOutputCalculationResultPoint] = UNSET
    __str__ = default_result_str

    def to_dict(self) -> Dict[str, Any]:
        """Dump `CloudPointCalculationResult` instance to a dict."""
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
        if success is not UNSET:
            field_dict["success"] = success
        if calculation_id is not UNSET:
            field_dict["calculationId"] = calculation_id
        if exception_info is not UNSET:
            field_dict["exceptionInfo"] = exception_info
        if profiling is not UNSET:
            field_dict["profiling"] = profiling
        if point is not UNSET:
            field_dict["point"] = point

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `CloudPointCalculationResult` instance from a dict."""
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
        point: Union[Unset, ApiOutputCalculationResultPoint]
        if isinstance(_point, Unset):
            point = UNSET
        else:
            point = ApiOutputCalculationResultPoint.from_dict(_point)

        cloud_point_calculation_result = cls(
            success=success,
            calculation_id=calculation_id,
            exception_info=exception_info,
            profiling=profiling,
            point=point,
        )

        return cloud_point_calculation_result
