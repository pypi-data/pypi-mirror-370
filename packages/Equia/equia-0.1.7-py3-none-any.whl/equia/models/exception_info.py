import datetime
from typing import Any, Dict, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExceptionInfo")


@attr.s(auto_attribs=True)
class ExceptionInfo:
    """Contains information for unexpected errors.

    Attributes
    ----------
    message_type : str
        The type of the error message.
    message : str
        The error message.
    stack_trace : str
        The stack trace of the error.
    date : datetime.datetime
        The date and time of the error.
    """
    message_type: Union[Unset, None, str] = UNSET
    message: Union[Unset, None, str] = UNSET
    stack_trace: Union[Unset, None, str] = UNSET
    date: Union[Unset, datetime.datetime] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ExceptionInfo` instance to a dict."""
        message_type = self.message_type
        message = self.message
        stack_trace = self.stack_trace
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if message_type is not UNSET:
            field_dict["messageType"] = message_type
        if message is not UNSET:
            field_dict["message"] = message
        if stack_trace is not UNSET:
            field_dict["stackTrace"] = stack_trace
        if date is not UNSET:
            field_dict["date"] = date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ExceptionInfo` instance from a dict."""
        d = src_dict.copy()
        message_type = d.pop("messageType", UNSET)

        message = d.pop("message", UNSET)

        stack_trace = d.pop("stackTrace", UNSET)

        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.datetime]
        if isinstance(_date, Unset):
            date = UNSET
        else:
            date = isoparse(_date)

        exception_info = cls(
            message_type=message_type,
            message=message,
            stack_trace=stack_trace,
            date=date,
        )

        return exception_info

    def __str__(self) -> str:
        """Return a string representation of the exception info."""
        parts = []

        if not isinstance(self.message_type, Unset) and self.message_type:
            parts.append(f"[{self.message_type}]")

        if not isinstance(self.message, Unset) and self.message:
            parts.append(self.message)

        if not isinstance(self.date, Unset) and self.date:
            parts.append(f"({self.date.isoformat()})")

        if not isinstance(self.stack_trace, Unset) and self.stack_trace:
            parts.append(f"\nStack trace:\n{self.stack_trace}")

        return " ".join(parts) if parts else "ExceptionInfo()"
