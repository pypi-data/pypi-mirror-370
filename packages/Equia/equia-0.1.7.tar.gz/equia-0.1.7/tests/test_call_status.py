from typing import Union
import pytest
from equia.models import (
    ProblemDetails,
    StatusInput, StatusResult
)
from equia.equia_client import EquiaClient
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_status():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: StatusInput = client.get_status_input()

    result: Union[StatusResult, ProblemDetails] = await client.call_status_get_async(input)

    await client.cleanup()

    # Print the result for debugging purposes
    if isinstance(result, ProblemDetails):
        print("Error:", result)
    
    #assert result.status == 400
    assert result.success is True
