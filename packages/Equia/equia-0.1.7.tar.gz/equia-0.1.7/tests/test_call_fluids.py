import pytest
from typing import Union
from equia.models import (
    ProblemDetails,
    FluidAddInput, FluidAddResult, 
    FluidGetInput, FluidGetResult, 
    FluidDeleteInput, FluidDeleteResult
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid1_nHexane_Ethylene_HDPE7 import demofluid1_nHexane_Ethylene_HDPE7
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_fluid():
    # Add fluid
    clientAdd = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    inputAdd: FluidAddInput = clientAdd.get_fluid_add_input()
    inputAdd.fluid = demofluid1_nHexane_Ethylene_HDPE7()

    resultAdd: Union[FluidAddResult, ProblemDetails] = await clientAdd.call_fluid_add_async(inputAdd)

    await clientAdd.cleanup()

    #assert result.status == 400
    print(resultAdd)
    if isinstance(resultAdd, ProblemDetails):
        print(resultAdd.exception_info)
        print(resultAdd.exception_info.message)
        print(resultAdd.exception_info.stack_trace)
    assert resultAdd.success is True

    # Get fluid    
    clientGet = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    inputGet: Union[FluidGetInput, ProblemDetails] = clientGet.get_fluid_get_input()
    inputGet.fluidid = resultAdd.fluidid

    resultGet: Union[FluidGetResult, ProblemDetails] = await clientGet.call_fluid_get_async(inputGet)

    await clientGet.cleanup()

    #assert result.status == 400
    assert resultGet.success is True
    assert len(resultGet.fluid.standards) == 2
    assert len(resultGet.fluid.polymers) == 1

    # Delete fluid
    clientDelete = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    inputDelete: Union[FluidDeleteInput, ProblemDetails] = clientDelete.get_fluid_delete_input()
    inputDelete.fluidid = resultAdd.fluidid

    resultDelete: Union[FluidDeleteResult, ProblemDetails] = await clientDelete.call_fluid_delete_async(inputDelete)

    await clientDelete.cleanup()

    #assert result.status == 400
    assert resultDelete.success is True
