import pytest
from typing import Union
from equia.models import (
    CalculationComposition, ProblemDetails, 
    EosPropertiesTPnCalculationInput, EosPropertiesTPnCalculationResult
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid1_nHexane_Ethylene_HDPE7 import demofluid1_nHexane_Ethylene_HDPE7
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_eospropertiestpn():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: EosPropertiesTPnCalculationInput = client.get_eospropertiestpn_input()
    input.temperature = 550
    input.pressure = 20
    input.components = [
        CalculationComposition(amount=0.78),
        CalculationComposition(amount=0.02),
        CalculationComposition(amount=0.20)
    ]
    input.pointtype = "Fixed Temperature/Pressure"

    input.fluid = demofluid1_nHexane_Ethylene_HDPE7()
    input.units = "C(In,Massfraction);C(Out,Massfraction);T(In,Kelvin);T(Out,Kelvin);P(In,Bar);P(Out,Bar);H(In,kJ/Kg);H(Out,kJ/Kg);S(In,kJ/(Kg Kelvin));S(Out,kJ/(Kg Kelvin));Cp(In,kJ/(Kg Kelvin));Cp(Out,kJ/(Kg Kelvin));Viscosity(In,centiPoise);Viscosity(Out,centiPoise);Surfacetension(In,N/m);Surfacetension(Out,N/m)"

    # Print the input for debugging purposes
    print(input)
    
    # Call the calculation
    result: Union[EosPropertiesTPnCalculationResult, ProblemDetails] = await client.call_eospropertiestpn_async(input)
    
    # Print the result for debugging purposes
    print(result)
    
    await client.cleanup()

    #assert result.status == 400
    assert result.success is True
    assert result.point.volume.units == 'cm3/mole'
    assert result.point.volume.value == 1604.1004460880863
    assert result.point.residual.volume.value == -682.3898039119135
    assert result.point.ideal.volume.value == 2286.49025
