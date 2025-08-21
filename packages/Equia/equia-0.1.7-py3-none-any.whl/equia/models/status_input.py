from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusInput")


@attr.s(auto_attribs=True)
class StatusInput:
    """Input for status.

    Attributes
    ----------
    access_key : str
        Access key for the API. This is used to authenticate the user.
    """
    access_key: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Dump `StatusInput` instance to a dict."""
        access_key = self.access_key

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessKey": access_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `StatusInput` instance from a dict."""
        d = src_dict.copy()

        access_key = d.pop("accessKey")

        request_status_input = cls(
            access_key=access_key
        )

        return request_status_input
