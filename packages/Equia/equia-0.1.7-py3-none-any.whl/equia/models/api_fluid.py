import json
import datetime
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.api_fluid_kij import ApiFluidKij
from ..models.api_fluid_polymer_component import ApiFluidPolymerComponent
from ..models.api_fluid_standard_component import ApiFluidStandardComponent
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluid")


@attr.s(auto_attribs=True)
class ApiFluid:
    """
    Equia fluid definition. To be used in the `fluid` attribute of calculation inputs.
    
    Attributes
    ----------
    fluidid : str
        Unique identifier for the fluid.
    creation_time : datetime.datetime
        Date and time the fluid was created.
    name : str
        Name of the fluid.
    comment : str
        Comment for the fluid.
    eos : str
        Equation of state for the fluid. 
        Options: `{'SRK', 'PR', 'PR78', 'PC-SAFT'}`
    property_reference_point : str
        Reference point for the fluid.
    solvent_cp : str
        Heat capacity model for the solvents.
    polymer_cp : str
        Heat capacity model for the polymers.
    standards : List[ApiFluidStandardComponent]
        Model parameters for each standard component.
    polymers : List[ApiFluidPolymerComponent]
        Model parameters for each polymer component.
    kij : List[ApiFluidKij]
        kij (or BIP, binary interactions parameters) for the fluid.
    """

    fluidid: Union[Unset, str] = UNSET
    creation_time: Union[Unset, datetime.datetime] = UNSET
    name: Union[Unset, None, str] = UNSET
    comment: Union[Unset, None, str] = UNSET
    eos: Union[Unset, str] = UNSET
    property_reference_point: Union[Unset, str] = UNSET
    solvent_cp: Union[Unset, str] = UNSET
    polymer_cp: Union[Unset, str] = UNSET
    standards: Union[Unset, None, List[ApiFluidStandardComponent]] = UNSET
    polymers: Union[Unset, None, List[ApiFluidPolymerComponent]] = UNSET
    kij: Union[Unset, None, List[ApiFluidKij]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluid` instance to a dict."""
        fluidid = self.fluidid
        creation_time: Union[Unset, str] = UNSET
        if not isinstance(self.creation_time, Unset):
            creation_time = self.creation_time.isoformat()

        name = self.name
        comment = self.comment
        eos = self.eos

        property_reference_point = self.property_reference_point

        solvent_cp = self.solvent_cp

        polymer_cp = self.polymer_cp

        standards: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.standards, Unset):
            if self.standards is None:
                standards = None
            else:
                standards = []
                for standards_item_data in self.standards:
                    standards_item = standards_item_data.to_dict()

                    standards.append(standards_item)

        polymers: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.polymers, Unset):
            if self.polymers is None:
                polymers = None
            else:
                polymers = []
                for polymers_item_data in self.polymers:
                    polymers_item = polymers_item_data.to_dict()

                    polymers.append(polymers_item)

        kij: Union[Unset, None, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.kij, Unset):
            if self.kij is None:
                kij = None
            else:
                kij = []
                for kij_item_data in self.kij:
                    kij_item = kij_item_data.to_dict()

                    kij.append(kij_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if not isinstance(fluidid, Unset):
            field_dict["fluidId"] = fluidid
        if not isinstance(creation_time, Unset):
            field_dict["creationTime"] = creation_time
        if not isinstance(name, Unset):
            field_dict["name"] = name
        if not isinstance(comment, Unset):
            field_dict["comment"] = comment
        if not isinstance(eos, Unset):
            field_dict["eos"] = eos
        if not isinstance(property_reference_point, Unset):
            field_dict["propertyReferencePoint"] = property_reference_point
        if not isinstance(solvent_cp, Unset):
            field_dict["solventCp"] = solvent_cp
        if not isinstance(polymer_cp, Unset):
            field_dict["polymerCp"] = polymer_cp
        if not isinstance(standards, Unset):
            field_dict["standards"] = standards
        if not isinstance(polymers, Unset):
            field_dict["polymers"] = polymers
        if not isinstance(kij, Unset):
            field_dict["kij"] = kij

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluid` instance from a dict."""
        d = src_dict.copy()
        fluidid = d.pop("fluidId", UNSET)

        _creation_time = d.pop("creationTime", UNSET)
        creation_time: Union[Unset, datetime.datetime]
        if isinstance(_creation_time, Unset):
            creation_time = UNSET
        else:
            creation_time = isoparse(_creation_time)

        name = d.pop("name", UNSET)

        comment = d.pop("comment", UNSET)

        eos = d.pop("eos", UNSET)

        property_reference_point = d.pop("propertyReferencePoint", UNSET)

        solvent_cp = d.pop("solventCp", UNSET)

        polymer_cp = d.pop("polymerCp", UNSET)

        standards = []
        _standards = d.pop("standards", UNSET)
        for standards_item_data in _standards or []:
            standards_item = ApiFluidStandardComponent.from_dict(standards_item_data)

            standards.append(standards_item)

        polymers = []
        _polymers = d.pop("polymers", UNSET)
        for polymers_item_data in _polymers or []:
            polymers_item = ApiFluidPolymerComponent.from_dict(polymers_item_data)

            polymers.append(polymers_item)

        kij = []
        _kij = d.pop("kij", UNSET)
        for kij_item_data in _kij or []:
            kij_item = ApiFluidKij.from_dict(kij_item_data)

            kij.append(kij_item)

        api_fluid = cls(
            fluidid=fluidid,
            creation_time=creation_time,
            name=name,
            comment=comment,
            eos=eos,
            property_reference_point=property_reference_point,
            solvent_cp=solvent_cp,
            polymer_cp=polymer_cp,
            standards=standards,
            polymers=polymers,
            kij=kij,
        )

        return api_fluid

    def to_json(self, path: Path = None) -> Union[str, None]:
        """Dump `ApiFluid` instance to a JSON string or file.
        
        Parameters
        ----------
        path : Path, optional
            If provided, the JSON string will be written to this path.
            Else the JSON string will be returned.
        """
        if path is None:
            return json.dumps(self.to_dict())
        else:
            try:
                path = Path(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w') as f:
                    json.dump(self.to_dict(), f)
            except Exception as e:
                print(e)

    @classmethod
    def from_json(cls: Type[T], path: Path) -> T:
        """Load `ApiFluid` instance from a JSON file.
        
        Parameters
        ----------
        path : Path
            Path to the JSON file.
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """
        Returns a string representation of the `ApiFluid` instance.

        Includes basic fluid metadata and a listing of standard components.
        """
        parts = []
        name = self.name if not isinstance(self.name, Unset) else 'N/A'
        fluidid = self.fluidid if not isinstance(self.fluidid, Unset) else 'N/A'
        created = self.creation_time.isoformat() if not isinstance(self.creation_time, Unset) else 'N/A'
        comment = self.comment if not isinstance(self.comment, Unset) else 'N/A'
        eos = self.eos if not isinstance(self.eos, Unset) else 'N/A'
        property_reference_point = self.property_reference_point if not isinstance(self.property_reference_point, Unset) else 'N/A'
        solvent_cp = self.solvent_cp if not isinstance(self.solvent_cp, Unset) else 'N/A'
        polymer_cp = self.polymer_cp if not isinstance(self.polymer_cp, Unset) else 'N/A'

        parts.append(f"Fluid: {name} (ID: {fluidid})")
        parts.append(f"  Created: {created}")
        parts.append(f"  Comment: {comment}")
        parts.append(f"  EOS: {eos}")
        parts.append(f"  Property Reference Point: {property_reference_point}")
        parts.append(f"  Solvent Cp: {solvent_cp}")
        parts.append(f"  Polymer Cp: {polymer_cp}")

        # Standard components
        if not isinstance(self.standards, Unset) and self.standards:
            parts.append("  Standard Components:")
            for s in self.standards:
                parts.append(f"    - {s}")
        else:
            parts.append("  Standard Components: None")

        # Polymer components
        if not isinstance(self.polymers, Unset) and self.polymers:
            parts.append("  Polymer Components:")
            for p in self.polymers:
                parts.append(f"    - {p}")
        else:
            parts.append("  Polymer Components: None")

        # Kij
        if not isinstance(self.kij, Unset) and self.kij:
            parts.append("  Kij:")
            for k in self.kij:
                parts.append(f"    - {k}")
        else:
            parts.append("  Kij: None")

        return "\n".join(parts)
