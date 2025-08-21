""" `units`

This module defines the `Units` class, which represents unit assignments for properties in flash calculations.
"""
import attr
from typing import Dict

@attr.s(auto_attribs=True)
class Units:
    """
    Represents unit assignments for properties in flash calculations.
    Users can pick a preset (SI, US, EU) or override individual units.
    
    Attributes
    ----------
    C_in : str
        Unit for composition (input). Options: `{"Massfraction", "Molefraction", "Masspercent", "Molepercent"}`.
    C_out : str
        Unit for composition (output). Options: `{"Massfraction", "Molefraction", "Masspercent", "Molepercent"}`.
    T_in : str
        Unit for temperature (input). Options: `{"Kelvin", "Celsius", "Fahrenheit", "Rankine"}`.
    T_out : str
        Unit for temperature (output). Options: `{"Kelvin", "Celsius", "Fahrenheit", "Rankine"}`.
    P_in : str
        Unit for pressure (input). Options: `{"Bar", "Atm", "Pa", "kPa", "MPa", "Psi", "Psig", "mmHg"}`.
    P_out : str
        Unit for pressure (output). Options: `{"Bar", "Atm", "Pa", "kPa", "MPa", "Psi", "Psig", "mmHg"}`.
    H_in : str
        Unit for enthalpy (input). Options: `{"kJ/Kg", "kJ/Ton", "kJ/kMol"}`.
    H_out : str
        Unit for enthalpy (output). Options: `{"kJ/Kg", "kJ/Ton", "kJ/kMol"}`.
    S_in : str
        Unit for entropy (input). Options: `{"kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"}`.
    S_out : str
        Unit for entropy (output). Options: `{"kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"}`.
    Cp_in : str
        Unit for heat capacity (input). Options: `{"kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"}`.
    Cp_out : str
        Unit for heat capacity (output). Options: `{"kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"}`.
    Viscosity_in : str
        Unit for viscosity (input). Options: `{"centiPoise"}`.
    Viscosity_out : str
        Unit for viscosity (output). Options: `{"centiPoise"}`.
    SurfaceTension_in : str
        Unit for surface tension (input). Options: `{"N/m"}`.
    SurfaceTension_out : str
        Unit for surface tension (output). Options: `{"N/m"}`.
    """
    C_in: str = attr.field(
        default="Massfraction",
        validator=attr.validators.in_(["Massfraction", "Molefraction", "Masspercent", "Molepercent"])
    )
    C_out: str = attr.field(
        default="Massfraction",
        validator=attr.validators.in_(["Massfraction", "Molefraction", "Masspercent", "Molepercent"])
    )
    T_in: str = attr.field(
        default="Kelvin",
        validator=attr.validators.in_(["Kelvin", "Celsius", "Fahrenheit", "Rankine"])
    )
    T_out: str = attr.field(
        default="Kelvin",
        validator=attr.validators.in_(["Kelvin", "Celsius", "Fahrenheit", "Rankine"])
    )
    P_in: str = attr.field(
        default="Bar",
        validator=attr.validators.in_(["Bar", "Atm", "Pa", "kPa", "MPa", "Psi", "Psig", "mmHg"])
    )
    P_out: str = attr.field(
        default="Bar",
        validator=attr.validators.in_(["Bar", "Atm", "Pa", "kPa", "MPa", "Psi", "Psig", "mmHg"])
    )
    H_in: str = attr.field(
        default="kJ/Kg",
        validator=attr.validators.in_(["kJ/Kg", "kJ/Ton", "kJ/kMol"])
    )
    H_out: str = attr.field(
        default="kJ/Kg",
        validator=attr.validators.in_(["kJ/Kg", "kJ/Ton", "kJ/kMol"])
    )
    S_in: str = attr.field(
        default="kJ/(Kg Kelvin)",
        validator=attr.validators.in_(["kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"])
    )
    S_out: str = attr.field(
        default="kJ/(Kg Kelvin)",
        validator=attr.validators.in_(["kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"])
    )
    Cp_in: str = attr.field(
        default="kJ/(Kg Kelvin)",
        validator=attr.validators.in_(["kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"])
    )
    Cp_out: str = attr.field(
        default="kJ/(Kg Kelvin)",
        validator=attr.validators.in_(["kJ/(Kg Kelvin)", "kJ/(Ton Kelvin)", "kJ/(kMol Kelvin)"])
    )
    Viscosity_in: str = attr.field(
        default="centiPoise",
        validator=attr.validators.in_(["centiPoise"])
    )
    Viscosity_out: str = attr.field(
        default="centiPoise",
        validator=attr.validators.in_(["centiPoise"])
    )
    Surfacetension_in: str = attr.field(
        default="N/m",
        validator=attr.validators.in_(["N/m"])
    )
    Surfacetension_out: str = attr.field(
        default="N/m",
        validator=attr.validators.in_(["N/m"])
    )

    @classmethod
    def SI(cls, **overrides: Dict[str, str]) -> "Units":
        """Returns `Units` with standard SI defaults, allowing overrides."""
        base = {
            "C_in": "Massfraction",     "C_out": "Massfraction",
            "T_in": "Kelvin",           "T_out": "Kelvin",
            "P_in": "Bar",              "P_out": "Bar",
            "H_in": "kJ/Kg",            "H_out": "kJ/Kg",
            "S_in": "kJ/(Kg Kelvin)",   "S_out": "kJ/(Kg Kelvin)",
            "Cp_in": "kJ/(Kg Kelvin)",  "Cp_out": "kJ/(Kg Kelvin)",
            "Viscosity_in": "centiPoise","Viscosity_out": "centiPoise",
            "Surfacetension_in": "N/m", "Surfacetension_out": "N/m",
        }
        base.update(overrides)
        return cls(**base)

    @classmethod
    def US(cls, **overrides: Dict[str, str]) -> "Units":
        """Returns US-style units: Fahrenheit & Psi, others same as SI."""
        return cls.SI(
            T_in="Fahrenheit",
            T_out="Fahrenheit",
            P_in="Psi",
            P_out="Psi",
            **overrides
        )

    @classmethod
    def EU(cls, **overrides: Dict[str, str]) -> "Units":
        """Returns European-style units: Celsius temps, others same as SI."""
        return cls.SI(
            T_in="Celsius",
            T_out="Celsius",
            **overrides
        )

    def __str__(self) -> str:
        """String representation: semicolon-separated unit assignments."""
        parts = [
            f"C(In,{self.C_in})", f"C(Out,{self.C_out})",
            f"T(In,{self.T_in})", f"T(Out,{self.T_out})",
            f"P(In,{self.P_in})", f"P(Out,{self.P_out})",
            f"H(In,{self.H_in})", f"H(Out,{self.H_out})",
            f"S(In,{self.S_in})", f"S(Out,{self.S_out})",
            f"Cp(In,{self.Cp_in})", f"Cp(Out,{self.Cp_out})",
            f"Viscosity(In,{self.Viscosity_in})", f"Viscosity(Out,{self.Viscosity_out})",
            f"Surfacetension(In,{self.Surfacetension_in})", f"Surfacetension(Out,{self.Surfacetension_out})",
        ]
        return ";".join(parts)

    def to_dict(self) -> Dict[str, str]:
        """Dump `Units` instance to a dict."""
        return {
            "C_in": self.C_in,
            "C_out": self.C_out,
            "T_in": self.T_in,
            "T_out": self.T_out,
            "P_in": self.P_in,
            "P_out": self.P_out,
            "H_in": self.H_in,
            "H_out": self.H_out,
            "S_in": self.S_in,
            "S_out": self.S_out,
            "Cp_in": self.Cp_in,
            "Cp_out": self.Cp_out,
            "Viscosity_in": self.Viscosity_in,
            "Viscosity_out": self.Viscosity_out,
            "Surfacetension_in": self.Surfacetension_in,
            "Surfacetension_out": self.Surfacetension_out,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Units":
        """Load `Units` instance from a dict."""
        return cls(**data)