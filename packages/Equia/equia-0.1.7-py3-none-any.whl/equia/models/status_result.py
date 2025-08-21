from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.exception_info import ExceptionInfo
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusResult")


@attr.s(auto_attribs=True)
class StatusResult:
    """Holds result for status.

    Attributes
    ----------
    success : bool
        Indicates if the request was successful.
    exception_info : ExceptionInfo
        Information about any exceptions that occurred during the request.
    """

    success: Union[Unset, bool] = UNSET
    exception_info: Union[Unset, ExceptionInfo] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `StatusResult` instance to a dict."""
        success = self.success

        exception_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exception_info, Unset):
            exception_info = self.exception_info.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if exception_info is not UNSET:
            field_dict["exceptionInfo"] = exception_info

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `StatusResult` instance from a dict."""
        d = src_dict.copy()
        success = d.pop("success", UNSET)

        _exception_info = d.pop("exceptionInfo", UNSET)
        exception_info: Union[Unset, ExceptionInfo]
        if isinstance(_exception_info, Unset):
            exception_info = UNSET
        else:
            exception_info = ExceptionInfo.from_dict(_exception_info)

        request_fluid_result = cls(
            success=success,
            exception_info=exception_info,
        )

        return request_fluid_result
