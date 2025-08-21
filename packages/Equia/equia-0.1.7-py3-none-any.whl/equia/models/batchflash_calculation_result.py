from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.api_output_calculation_result_point import ApiOutputCalculationResultPoint
from ..models.api_profile_information import ApiProfileInformation
from ..models.exception_info import ExceptionInfo
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchFlashCalculationResult")


@attr.s(auto_attribs=True)
class BatchFlashCalculationResult:
    """Holds calculation result for a series of points.

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
    points : List[ApiOutputCalculationResultPoint]
        Calculation result for each point.
    """
    success: Union[Unset, bool] = UNSET
    calculation_id: Union[Unset, None, str] = UNSET
    exception_info: Union[Unset, ExceptionInfo] = UNSET
    profiling: Union[Unset, ApiProfileInformation] = UNSET
    points: List[ApiOutputCalculationResultPoint] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `BatchFlashCalculationResult` instance to a dict."""
        success = self.success
        calculation_id = self.calculation_id
        exception_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exception_info, Unset):
            exception_info = self.exception_info.to_dict()

        profiling: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.profiling, Unset):
            profiling = self.profiling.to_dict()

        points = []
        for item_data in self.points:
            item = item_data.to_dict()
            points.append(item)

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
        if points is not UNSET:
            field_dict["points"] = points

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `BatchFlashCalculationResult` instance from a dict."""
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

        points = []
        _points = d.pop("points")
        for item_data in _points:
            item = ApiOutputCalculationResultPoint.from_dict(item_data)
            points.append(item)

        batchflash_calculation_result = cls(
            success=success,
            calculation_id=calculation_id,
            exception_info=exception_info,
            profiling=profiling,
            points=points,
        )

        return batchflash_calculation_result
