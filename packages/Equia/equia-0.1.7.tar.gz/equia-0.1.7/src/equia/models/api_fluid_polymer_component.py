from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.api_fluid_component_block import ApiFluidComponentBlock
from ..models.api_fluid_pseudo_component import ApiFluidPseudoComponent
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluidPolymerComponent")


@attr.s(auto_attribs=True)
class ApiFluidPolymerComponent:
    """Information for a fluid component.
    
    Stores the parameters for a *polymer* component, which is to be stored in the `ApiFluid.polymers` attribute.
    
    Attributes
    ----------
    formula : str
        Formula of the polymer component.
    short_name : str
        Short name of the polymer component.
    sorting_order : int
        Index for sorting the polymer components.
    pseudo_components : List[ApiFluidPseudoComponent]
        Pseudo components for the polymer component.
    blocks : List[ApiFluidComponentBlock]
        Component blocks for the polymer component.
    """

    formula: Union[Unset, None, str] = UNSET
    short_name: Union[Unset, None, str] = UNSET
    sorting_order: Union[Unset, int] = UNSET
    pseudo_components: Union[Unset, None, List[ApiFluidPseudoComponent]] = UNSET
    blocks: Union[Unset, None, List[ApiFluidComponentBlock]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluidPolymerComponent` instance to a dict."""
        formula = self.formula
        short_name = self.short_name
        sorting_order = self.sorting_order

        pseudo_components: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.pseudo_components, Unset):
            if self.pseudo_components is None:
                pseudo_components = None
            else:
                pseudo_components = []
                for pseudo_components_item_data in self.pseudo_components:
                    pseudo_components_item = pseudo_components_item_data.to_dict()

                    pseudo_components.append(pseudo_components_item)

        blocks: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.blocks, Unset):
            if self.blocks is None:
                blocks = None
            else:
                blocks = []
                for blocks_item_data in self.blocks:
                    blocks_item = blocks_item_data.to_dict()

                    blocks.append(blocks_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if formula is not UNSET:
            field_dict["formula"] = formula
        if short_name is not UNSET:
            field_dict["shortName"] = short_name
        if sorting_order is not UNSET:
            field_dict["sortingOrder"] = sorting_order
        if pseudo_components is not UNSET:
            field_dict["pseudoComponents"] = pseudo_components
        if blocks is not UNSET:
            field_dict["blocks"] = blocks

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluidPolymerComponent` instance from a dict."""
        d = src_dict.copy()
        formula = d.pop("formula", UNSET)

        short_name = d.pop("shortName", UNSET)

        sorting_order = d.pop("sortingOrder", UNSET)

        pseudo_components = []
        _pseudo_components = d.pop("pseudoComponents", UNSET)
        for pseudo_components_item_data in _pseudo_components or []:
            pseudo_components_item = ApiFluidPseudoComponent.from_dict(pseudo_components_item_data)

            pseudo_components.append(pseudo_components_item)

        blocks = []
        _blocks = d.pop("blocks", UNSET)
        for blocks_item_data in _blocks or []:
            blocks_item = ApiFluidComponentBlock.from_dict(blocks_item_data)

            blocks.append(blocks_item)

        api_fluid_polymer_component = cls(
            formula=formula,
            short_name=short_name,
            sorting_order=sorting_order,
            pseudo_components=pseudo_components,
            blocks=blocks,
        )

        return api_fluid_polymer_component

    def __str__(self) -> str:
        """
        Returns a compact string representation of the ApiFluidPolymerComponent instance.

        Includes: formula, short name, sorting order, and counts of pseudo components and blocks (if defined).
        """
        parts = []

        if not isinstance(self.short_name, Unset) and self.short_name:
            parts.append(f"short_name={self.short_name}")
        if not isinstance(self.formula, Unset) and self.formula:
            parts.append(f"formula={self.formula}")
        if not isinstance(self.sorting_order, Unset):
            parts.append(f"sorting_order={self.sorting_order}")
        if not isinstance(self.pseudo_components, Unset) and self.pseudo_components is not None:
            parts.append(f"pseudo_components={len(self.pseudo_components)}")
        if not isinstance(self.blocks, Unset) and self.blocks is not None:
            parts.append(f"blocks={len(self.blocks)}")

        return ", ".join(parts)
