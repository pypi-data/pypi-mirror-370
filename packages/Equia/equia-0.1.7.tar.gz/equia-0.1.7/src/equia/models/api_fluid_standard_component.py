""" 
Class stores standard component metadata, including PC-SAFT parameters and thermodynamic constants.
"""
from typing import Any, Dict, Type, TypeVar, Union
import attr
from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiFluidStandardComponent")

# Mapping from attribute name to VLXE API key
ATTRIBUTE_MAPPING: Dict[str, str] = {
    # general component data
    "formula": "formula",
    "dippr_database_id": "dipprDatabaseId",
    "name": "name",
    "is_alkane": "isAlkane",
    "sorting_order": "sortingOrder",
    "molar_mass": "molarMass",
    "critical_temperature": "criticalTemperature",
    "critical_pressure": "criticalPressure",
    "critical_volume": "criticalVolume",
    "acentric_factor": "acentricFactor",
    # model parameter data
    "volume_shift": "volumeShift",
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
    # heat capacity coefficients
    "cp_ig_poly_c0": "CpIgPolyC0",
    "cp_ig_poly_c1": "CpIgPolyC1",
    "cp_ig_poly_c2": "CpIgPolyC2",
    "cp_ig_poly_c3": "CpIgPolyC3",
    "cp_ig_poly_c4": "CpIgPolyC4",
    "cp_ig_poly_c5": "CpIgPolyC5",
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
class ApiFluidStandardComponent:
    """Information for a standard fluid component.

    Stores the parameters for a *standard* component, which is to be stored in the `ApiFluid.standards` attribute.
    
    Attributes
    ----------
    formula : str
        Formula of the standard component.
    dippr_database_id : int
        Dippr database id of the standard component.
    name : str
        Name of the standard component.
    is_alkane : bool
        Whether the standard component is an alkane.
    sorting_order : int
        Index for sorting the standard components.
    molar_mass : float
        Molar mass (g/mol) of the standard component.
    critical_temperature : float
        Critical temperature (K) of the standard component.
    critical_pressure : float
        Critical pressure (bar) of the standard component.
    critical_volume : float
        Critical volume (cm^3/mol) of the standard component.
    acentric_factor : float
        Acentric factor (-) of the standard component.
    volume_shift : float
        Volume shift (cm3/g) of the standard component.
    pc_saft_epsilon : float
        PC-SAFT epsilon (K) of the standard component.
    pc_saft_sigma_0 : float
        PC-SAFT sigma_0 (Angstrom) of the standard component.
    pc_saft_sigma_1 : float
        PC-SAFT sigma_1 (Angstrom) of the standard component.
    pc_saft_sigma_2 : float
        PC-SAFT sigma_2 (1/K) of the standard component.
    pc_saft_sigma_3 : float
        PC-SAFT sigma_3 (Angstrom) of the standard component.
    pc_saft_sigma_4 : float
        PC-SAFT sigma_4 (1/K) of the standard component.
    pc_saftdm : float
        PC-SAFT dm (mol/g) of the standard component.
    pc_saft_ab_active : bool
        PC-SAFT association active of the standard component.
    pc_saft_ab_kappa : float
        PC-SAFT association bond volume (-) of the standard component.
    pc_saft_ab_epsilon : float
        PC-SAFT association energy (K) of the standard component.
    pc_saft_ab_scheme : str
        PC-SAFT association scheme (-) of the standard component.
    pc_saft_polar_active : bool
        PC-SAFT polar active of the standard component.
    pc_saft_polarx : float
        PC-SAFT polar x (-) of the standard component.
    pc_saft_polar_d : float
        PC-SAFT polar dipole strength (D) of the standard component.
    cp_ig_poly_c[i] : float
        Ideal gas heat capacity polynomial coefficients of the standard component.
    cp_ig_dippr_c[i] : float
        Ideal gas heat capacity DIPPR coefficients of the standard component.
    ideal_gas_gibbs_energy_of_formation : float
        Ideal gas Gibbs energy of formation (kJ/kg) of the standard component.
    ideal_gas_enthalpy_of_formation : float
        Ideal gas Enthalpy of formation (kJ/kg) of the standard component.
    """
    # General component data
    formula: Union[Unset, None, str] = UNSET
    dippr_database_id: Union[Unset, int] = UNSET
    name: Union[Unset, None, str] = UNSET
    is_alkane: Union[Unset, bool] = UNSET
    sorting_order: Union[Unset, int] = UNSET
    molar_mass: Union[Unset, float] = UNSET
    critical_temperature: Union[Unset, float] = UNSET
    critical_pressure: Union[Unset, float] = UNSET
    critical_volume: Union[Unset, float] = UNSET
    acentric_factor: Union[Unset, float] = UNSET
    # Model parameter data
    volume_shift: Union[Unset, float] = UNSET
    pc_saft_epsilon: Union[Unset, float] = UNSET
    pc_saft_sigma_0: Union[Unset, float] = UNSET
    pc_saft_sigma_1: Union[Unset, float] = UNSET
    pc_saft_sigma_2: Union[Unset, float] = UNSET
    pc_saft_sigma_3: Union[Unset, float] = UNSET
    pc_saft_sigma_4: Union[Unset, float] = UNSET
    pc_saftdm: Union[Unset, float] = UNSET
    pc_saft_ab_active: Union[Unset, bool] = UNSET
    pc_saft_ab_kappa: Union[Unset, float] = UNSET
    pc_saft_ab_epsilon: Union[Unset, float] = UNSET
    pc_saft_ab_scheme: Union[Unset, str] = UNSET
    pc_saft_polar_active: Union[Unset, bool] = UNSET
    pc_saft_polarx: Union[Unset, float] = UNSET
    pc_saft_polar_d: Union[Unset, float] = UNSET
    # Heat capacity coefficients
    cp_ig_poly_c0: Union[Unset, float] = UNSET
    cp_ig_poly_c1: Union[Unset, float] = UNSET
    cp_ig_poly_c2: Union[Unset, float] = UNSET
    cp_ig_poly_c3: Union[Unset, float] = UNSET
    cp_ig_poly_c4: Union[Unset, float] = UNSET
    cp_ig_poly_c5: Union[Unset, float] = UNSET
    cp_ig_poly_c6: Union[Unset, float] = UNSET
    cp_ig_poly_c7: Union[Unset, float] = UNSET
    cp_ig_dippr_c0: Union[Unset, float] = UNSET
    cp_ig_dippr_c1: Union[Unset, float] = UNSET
    cp_ig_dippr_c2: Union[Unset, float] = UNSET
    cp_ig_dippr_c3: Union[Unset, float] = UNSET
    cp_ig_dippr_c4: Union[Unset, float] = UNSET
    cp_ig_dippr_c5: Union[Unset, float] = UNSET
    cp_ig_dippr_c6: Union[Unset, float] = UNSET
    # Thermodynamic constants
    ideal_gas_gibbs_energy_of_formation: Union[Unset, float] = UNSET
    ideal_gas_enthalpy_of_formation: Union[Unset, float] = UNSET
    extra_attrs : Union[Unset, Dict[str, Any]] = UNSET   # Extra attributes not explicitly defined in the class

    def to_dict(self) -> Dict[str, Any]:
        """Dump `ApiFluidStandardComponent` instance to a dict."""
        result: Dict[str, Any] = {}
        for attr_name, json_key in ATTRIBUTE_MAPPING.items():
            val = getattr(self, attr_name)
            if not isinstance(val, Unset):
                result[json_key] = val
        return result

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `ApiFluidStandardComponent` instance from a dict."""
        reverse_map = {v: k for k, v in ATTRIBUTE_MAPPING.items()}
        kwargs = {
            attr_name: src_dict.get(json_key, UNSET)
            for json_key, attr_name in reverse_map.items()
        }
        return cls(**kwargs)
    
    def __str__(self) -> str:
        """
        Returns a compact string representation of the `ApiFluidStandardComponent` instance.
        
        Includes only attributes that are not `Unset`.
        """
        items = []
        for attr_name, json_key in ATTRIBUTE_MAPPING.items():
            val = getattr(self, attr_name)
            if not isinstance(val, Unset):
                items.append(f"{attr_name}={val}")
        return ", ".join(items)
