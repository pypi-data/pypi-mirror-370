from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiProfileTimeInformation")


@attr.s(auto_attribs=True)
class ApiProfileTimeInformation:
    """Time information used in profiling.
    
    Attributes
    ----------
    time : str
        Time.
    milli_seconds : int
        Milliseconds.
    step : str
        Step.
    micro_service : str
        Micro service.
    sorting_order : int
        Sorting order.
    """
    time: Union[Unset, None, str] = UNSET
    milli_seconds: Union[Unset, int] = UNSET
    step: Union[Unset, None, str] = UNSET
    micro_service: Union[Unset, None, str] = UNSET
    sorting_order: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiProfileTimeInformation` instance to a dict."""
        time = self.time
        milli_seconds = self.milli_seconds
        step = self.step
        micro_service = self.micro_service
        sorting_order = self.sorting_order

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if time is not UNSET:
            field_dict["Time"] = time
        if milli_seconds is not UNSET:
            field_dict["milliSeconds"] = milli_seconds
        if step is not UNSET:
            field_dict["step"] = step
        if micro_service is not UNSET:
            field_dict["microService"] = micro_service
        if sorting_order is not UNSET:
            field_dict["sortingOrder"] = sorting_order

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiProfileTimeInformation` instance from a dict."""
        d = src_dict.copy()
        time = d.pop("Time", UNSET)

        milli_seconds = d.pop("milliSeconds", UNSET)

        step = d.pop("step", UNSET)

        micro_service = d.pop("microService", UNSET)

        sorting_order = d.pop("sortingOrder", UNSET)

        api_profile_time_information = cls(
            time=time,
            milli_seconds=milli_seconds,
            step=step,
            micro_service=micro_service,
            sorting_order=sorting_order,
        )

        return api_profile_time_information
