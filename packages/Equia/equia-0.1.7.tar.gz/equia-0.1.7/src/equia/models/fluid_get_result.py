from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_fluid import ApiFluid
from ..models.exception_info import ExceptionInfo
from ..types import UNSET, Unset

T = TypeVar("T", bound="FluidGetResult")


@attr.s(auto_attribs=True)
class FluidGetResult:
    """Holds result for requesting information for a fluid.

    Attributes
    ----------
    success : bool
        Indicates if the request was successful.
    fluid : ApiFluid
        Fluid information.
    exception_info : ExceptionInfo
        Information about any exceptions that occurred during the request.
    """
    success: Union[Unset, bool] = UNSET
    fluid: Union[Unset, ApiFluid] = UNSET
    exception_info: Union[Unset, ExceptionInfo] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `FluidGetResult` instance to a dict."""
        success = self.success

        fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fluid, Unset):
            fluid = self.fluid.to_dict()

        exception_info: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.exception_info, Unset):
            exception_info = self.exception_info.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if fluid is not UNSET:
            field_dict["fluid"] = fluid
        if exception_info is not UNSET:
            field_dict["exceptionInfo"] = exception_info

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `FluidGetResult` instance from a dict."""
        d = src_dict.copy()
        success = d.pop("success", UNSET)

        _fluid = d.pop("fluid", UNSET)
        fluid: Union[Unset, ApiFluid]
        if isinstance(_fluid, Unset):
            fluid = UNSET
        else:
            fluid = ApiFluid.from_dict(_fluid)

        _exception_info = d.pop("exceptionInfo", UNSET)
        exception_info: Union[Unset, ExceptionInfo]
        if isinstance(_exception_info, Unset):
            exception_info = UNSET
        else:
            exception_info = ExceptionInfo.from_dict(_exception_info)

        request_fluid_result = cls(
            success=success,
            fluid=fluid,
            exception_info=exception_info,
        )

        return request_fluid_result
