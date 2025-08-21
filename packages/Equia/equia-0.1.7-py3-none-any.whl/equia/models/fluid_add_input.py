from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.api_fluid import ApiFluid
from ..types import UNSET, Unset

T = TypeVar("T", bound="FluidAddInput")


@attr.s(auto_attribs=True)
class FluidAddInput:
    """Input for adding new fluid to database.

    Attributes
    ----------
    access_key : str
        Access key for the API. This is used to authenticate the user.
    fluid : ApiFluid
        Fluid information.
    """
    access_key: str
    fluid: Union[Unset, ApiFluid] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `FluidAddInput` instance to a dict."""
        access_key = self.access_key
        fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fluid, Unset):
            fluid = self.fluid.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessKey": access_key,
            }
        )
        if not isinstance(fluid, Unset):
            field_dict["fluid"] = fluid

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `FluidAddInput` instance from a dict."""
        d = src_dict.copy()

        access_key = d.pop("accessKey")

        _fluid = d.pop("fluid", UNSET)
        fluid: Union[Unset, ApiFluid]
        if isinstance(_fluid, Unset):
            fluid = UNSET
        else:
            fluid = ApiFluid.from_dict(_fluid)

        new_fluid_input = cls(
            access_key=access_key,
            fluid=fluid,
        )

        return new_fluid_input
