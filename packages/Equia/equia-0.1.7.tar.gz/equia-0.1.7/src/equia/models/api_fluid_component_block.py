""" 
Class stores block component metadata, including PC-SAFT parameters and thermodynamic constants.
"""
from typing import Any, Dict, Type, TypeVar, Union
import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluidComponentBlock")

# Mapping from attribute name to VLXE API key
ATTRIBUTE_MAPPING: Dict[str, str] = {
    # general component data
    "sorting_order": "sortingOrder",
    "block_massfraction": "blockMassfraction",
    "block_name": "blockName",
    "monomer_name": "monomerName",
    "monomer_molar_mass": "monomerMolarMass",
    # model parameter data
    "pc_saft_epsilon": "pcSaftEpsilon",
    "pc_saft_sigma_0": "pcSaftSigma0",
    "pc_saft_sigma_1": "pcSaftSigma1",
    "pc_saft_sigma_2": "pcSaftSigma2",
    "pc_saft_sigma_3": "pcSaftSigma3",
    "pc_saft_sigma_4": "pcSaftSigma4",
    "pc_saftdm": "pcSaftdm",
    "pc_saft_ab_active": "pcSaftAbActive",
    "pc_saft_ab_kappa": "pcSaftAbKappa",
    "pc_saft_ab_epsilon": "pcSaftAbEpsilon",
    "pc_saft_ab_scheme": "pcSaftAbScheme",
    "pc_saft_polar_active": "pcSaftPolarActive",
    "pc_saft_polarx": "pcSaftPolarx",
    "pc_saft_polar_d": "pcSaftPolarD",
    "sle_c": "sleC",
    "sle_hu": "sleHu",
    "sle_density_amorphous": "sleDensityAmorphous",
    "sle_density_crystalline": "sleDensityCrystalline",
    "sle_tss": "sleTss",
    "sle_hss": "sleHss",
    # heat capacity coefficients
    "cp_ig_poly_c0": "CpIgPolyC0",
    "cp_ig_poly_c1": "CpIgPolyC1",
    "cp_ig_poly_c2": "CpIgPolyC2",
    "cp_ig_poly_c3": "CpIgPolyC3",
    "cp_ig_poly_c4": "CpIgPolyC4",
    "cp_ig_poly_c5": "CpIgPolyC5",
    "cp_ig_poly_c6": "CpIgPolyC6",
    "cp_ig_poly_c7": "CpIgPolyC7",
    "cp_ig_dippr_c0": "CpIgDipprC0",
    "cp_ig_dippr_c1": "CpIgDipprC1",
    "cp_ig_dippr_c2": "CpIgDipprC2",
    "cp_ig_dippr_c3": "CpIgDipprC3",
    "cp_ig_dippr_c4": "CpIgDipprC4",
    "cp_ig_dippr_c5": "CpIgDipprC5",
    "cp_ig_dippr_c6": "CpIgDipprC6",
    # thermodynamic constants
    "ideal_gas_gibbs_energy_of_formation": "IdealGasGibbsEnergyOfFormation",
    "ideal_gas_enthalpy_of_formation": "IdealGasEnthalpyOfFormation",
}


@attr.s(auto_attribs=True)
class ApiFluidComponentBlock:
    """
    Values for a component block.

    Attributes
    ----------
    sorting_order : int
        Sorting order for the component block.
    block_massfraction : float
        Mass fraction of the component block.
    block_name : str
        Name of the component block.
    monomer_name : str
        Name of the monomer.
    monomer_molar_mass : float
        Molar mass of the monomer.
    pc_saft_epsilon : float
        Segment interaction energy (K) of the component block.
    pc_saft_sigma_i : float
        Segment diameter (A) of the component block.
    pc_saftdm : float
        Ratio of segment number to molar mass for the component block.
    pc_saft_ab_active : bool
        Association active for the component block.
    pc_saft_ab_kappa : float
        Association volume (-) of the component block.
    pc_saft_ab_epsilon : float
        Association energy (K) of the component block.
    pc_saft_ab_scheme : str
        Association scheme of the component block.
    pc_saft_polar_active : bool
        Polar active for the component block.
    pc_saft_polarx : float
        Polar x parameter (-) of the component block.
    pc_saft_polar_d : float
        Dipolar moment (Debye) of the component block.
    sle_c : float
        SLE c parameter (-) of the component block.
    sle_hu : float
        SLE Hu parameter (-) of the component block.
    sle_density_amorphous : float
        SLE density amorphous (g/cm^3) of the component block.
    sle_density_crystalline : float
        SLE density crystalline (g/cm^3) of the component block.
    sle_tss : float
        SLE tss parameter (-) of the component block.
    sle_hss : float
        SLE hss parameter (-) of the component block.
    cp_ig_poly_c[i] : float
        Ideal gas heat capacity polynomial coefficients of the component block. 
    cp_ig_dippr_c[i] : float
        Ideal gas heat capacity dippr coefficients of the component block.
    ideal_gas_gibbs_energy_of_formation : float
        Ideal gas gibbs energy of formation (kJ/kg) of the component block.
    ideal_gas_enthalpy_of_formation : float
        Ideal gas enthalpy of formation (kJ/kg) of the component block.
    """
    # General component data
    sorting_order:    Union[Unset, int]   = UNSET
    block_massfraction: float = UNSET
    block_name:      Union[Unset, None, str] = UNSET
    monomer_name:    Union[Unset, None, str] = UNSET
    monomer_molar_mass: float = UNSET
    # Model parameter data
    pc_saft_epsilon: float = UNSET
    pc_saft_sigma_0: float = UNSET
    pc_saft_sigma_1: float = UNSET
    pc_saft_sigma_2: float = UNSET
    pc_saft_sigma_3: float = UNSET
    pc_saft_sigma_4: float = UNSET
    pc_saftdm:      float = UNSET
    pc_saft_ab_active: bool = UNSET
    pc_saft_ab_kappa: float = UNSET
    pc_saft_ab_epsilon: float = UNSET
    pc_saft_ab_scheme: str   = UNSET
    pc_saft_polar_active: bool  = UNSET
    pc_saft_polarx: float = UNSET
    pc_saft_polar_d: float = UNSET
    sle_c:            float = UNSET
    sle_hu:           float = UNSET
    sle_density_amorphous:  float = UNSET
    sle_density_crystalline: float = UNSET
    sle_tss:           float = UNSET
    sle_hss:           float = UNSET
    # Heat capacity coefficients
    cp_ig_poly_c0: float = UNSET
    cp_ig_poly_c1: float = UNSET
    cp_ig_poly_c2: float = UNSET
    cp_ig_poly_c3: float = UNSET
    cp_ig_poly_c4: float = UNSET
    cp_ig_poly_c5: float = UNSET
    cp_ig_poly_c6: float = UNSET
    cp_ig_poly_c7: float = UNSET
    cp_ig_dippr_c0: float = UNSET
    cp_ig_dippr_c1: float = UNSET
    cp_ig_dippr_c2: float = UNSET
    cp_ig_dippr_c3: float = UNSET
    cp_ig_dippr_c4: float = UNSET
    cp_ig_dippr_c5: float = UNSET
    cp_ig_dippr_c6: float = UNSET
    # Thermodynamic constants
    ideal_gas_gibbs_energy_of_formation: float = UNSET
    ideal_gas_enthalpy_of_formation:    float = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluidComponentBlock` instance to a dict."""
        result: Dict[str, Any] = {}
        for attr_name, json_key in ATTRIBUTE_MAPPING.items():
            value = getattr(self, attr_name)
            if value is not UNSET:
                result[json_key] = value
        return result

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluidComponentBlock` instance from a dict."""
        d = src_dict.copy()
        init_kwargs: Dict[str, Any] = {}
        for attr_name, json_key in ATTRIBUTE_MAPPING.items():
            init_kwargs[attr_name] = d.pop(json_key, UNSET)
        return cls(**init_kwargs)

    def __str__(self) -> str:
        """
        Returns a compact string representation of the `ApiFluidComponentBlock` instance.
        
        Includes only attributes that are not `Unset`.
        """
        items = []
        for attr_name, json_key in ATTRIBUTE_MAPPING.items():
            val = getattr(self, attr_name)
            if not isinstance(val, Unset):
                items.append(f"{attr_name}={val}")
        return ", ".join(items)
