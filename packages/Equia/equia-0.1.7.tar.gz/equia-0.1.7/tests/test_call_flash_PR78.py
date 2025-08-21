import pytest
from typing import Union
from equia.models import (
    CalculationComposition, ProblemDetails,
    FlashCalculationInput, FlashCalculationResult, 
    ApiOutputCalculationResultPoint,
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid_Methane_nHexane_Toluene import demofluid_Methane_nHexane_Toluene
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_flash_PR78():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: FlashCalculationInput = client.get_flash_input()
    input.temperature = 25
    input.pressure = 10
    input.components = [
        CalculationComposition(amount=0.10),
        CalculationComposition(amount=0.50),
        CalculationComposition(amount=0.40)
    ]
    input.flashtype = "FixedTemperaturePressure"

    input.fluid = demofluid_Methane_nHexane_Toluene(is_volume_shift=True)
    input.units = "C(In,Massfraction);C(Out,Massfraction);T(In,Celsius);T(Out,Celsius);P(In,Bar);P(Out,Bar);H(In,kJ/Kg);H(Out,kJ/Kg);S(In,kJ/(Kg Kelvin));S(Out,kJ/(Kg Kelvin));Cp(In,kJ/(Kg Kelvin));Cp(Out,kJ/(Kg Kelvin));Viscosity(In,centiPoise);Viscosity(Out,centiPoise);Surfacetension(In,N/m);Surfacetension(Out,N/m)"

    # Print the input for debugging purposes
    print(input)
    
    # Call the flash calculation asynchronously
    result: Union[FlashCalculationResult, ProblemDetails] = await client.call_flash_async(input)
    
    # Print the result for debugging purposes
    print(result)
    
    if result.success:
        print("Flash calculation was successful.")
        point: ApiOutputCalculationResultPoint = result.point
        print(point.phases_to_calculation_composition())
    
    await client.cleanup()

    #assert result.status == 400
    assert result.success
    assert len(result.point.phases) == 3
