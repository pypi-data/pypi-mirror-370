import pytest
from typing import Union
from equia.models import (
    CalculationComposition, ProblemDetails,
    FlashCalculationInput, FlashCalculationResult
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid1_nHexane_Ethylene_HDPE7 import demofluid1_nHexane_Ethylene_HDPE7
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_flash():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: FlashCalculationInput = client.get_flash_input()
    input.temperature = 445
    input.pressure = 20
    input.components = [
        CalculationComposition(amount=0.78),
        CalculationComposition(amount=0.02),
        CalculationComposition(amount=0.20)
    ]
    input.flashtype = "FixedTemperaturePressure"

    input.fluid = demofluid1_nHexane_Ethylene_HDPE7()
    input.units = "C(In,Massfraction);C(Out,Massfraction);T(In,Kelvin);T(Out,Kelvin);P(In,Bar);P(Out,Bar);H(In,kJ/Kg);H(Out,kJ/Kg);S(In,kJ/(Kg Kelvin));S(Out,kJ/(Kg Kelvin));Cp(In,kJ/(Kg Kelvin));Cp(Out,kJ/(Kg Kelvin));Viscosity(In,centiPoise);Viscosity(Out,centiPoise);Surfacetension(In,N/m);Surfacetension(Out,N/m)"

    # Print the input for debugging purposes
    print(input)
    
    # Call the flash calculation asynchronously
    result: Union[FlashCalculationResult, ProblemDetails] = await client.call_flash_async(input)

    # Print the result for debugging purposes
    print(result)
    
    await client.cleanup()

    #assert result.status == 400
    assert result.success
    assert len(result.point.phases) == 4
