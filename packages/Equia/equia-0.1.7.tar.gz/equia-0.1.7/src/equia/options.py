""" `options`

Allowable specifications for flash calculations.
"""

from enum import Enum

class ToStrEnum(str, Enum):
    """Enum whose values are always strings, and which can validate+return .value."""
    @classmethod
    def to_str(cls, val: "ToStrEnum") -> str:
        # will raise if val isn’t a valid member
        return cls(val).value

class FlashType(ToStrEnum):
    """Allowable flash calculation specifications: `{'FixedTemperaturePressure', 'FixedPressureEnthalpy', 'FixedPressureEntropy', 'FixedTemperatureVolume'}`."""
    FixedTemperaturePressure    = "FixedTemperaturePressure"
    FixedPressureEnthalpy       = "FixedPressureEnthalpy"
    FixedPressureEntropy        = "FixedPressureEntropy"
    FixedTemperatureVolume      = "FixedTemperatureVolume"

class CloudPointType(ToStrEnum):
    """Allowable cloud point calculation specifications: `{'FixedTemperature', 'FixedPressure'}`."""
    FixedTemperature    = "FixedTemperature"
    FixedPressure       = "FixedPressure"

class SlePointType(ToStrEnum):
    """Allowable SLE point calculation specifications: `{'FixedPressure', 'FixedTemperaturePressure'}`."""
    FixedPressure       = "FixedPressure"
    FixedTemperaturePressure    = "FixedTemperaturePressure"

class VolumeType(ToStrEnum):
    """Allowable volume calculation specifications: `{'Auto', 'Liquid', 'Vapor'}`."""
    Auto = 'Auto'
    Liquid = 'Liquid'
    Vapor = 'Vapor'
