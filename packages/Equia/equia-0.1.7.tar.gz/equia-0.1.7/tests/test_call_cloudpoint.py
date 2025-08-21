import pytest
from typing import Union
from equia.models import (
    CalculationComposition, ProblemDetails,
    CloudPointCalculationInput, CloudPointCalculationResult
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid1_nHexane_Ethylene_HDPE7 import demofluid1_nHexane_Ethylene_HDPE7
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_cloudpoint():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: CloudPointCalculationInput = client.get_cloud_point_input()
    input.fluid = demofluid1_nHexane_Ethylene_HDPE7()
    input.pressure = 30
    input.pointtype = "FixedPressure"
    input.components = [
        CalculationComposition(amount=0.78),
        CalculationComposition(amount=0.02),
        CalculationComposition(amount=0.20)
    ]
    input.units = "C(In,Massfraction);C(Out,Massfraction);T(In,Kelvin);T(Out,Kelvin);P(In,Bar);P(Out,Bar);H(In,kJ/Kg);H(Out,kJ/Kg);S(In,kJ/(Kg Kelvin));S(Out,kJ/(Kg Kelvin));Cp(In,kJ/(Kg Kelvin));Cp(Out,kJ/(Kg Kelvin));Viscosity(In,centiPoise);Viscosity(Out,centiPoise);Surfacetension(In,N/m);Surfacetension(Out,N/m)"

    result: Union[CloudPointCalculationResult, ProblemDetails] = await client.call_cloud_point_async(input)

    await client.cleanup()

    #assert result.status == 400
    assert result.success is True
    assert len(result.point.phases) == 2
