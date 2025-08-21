import aiohttp
from typing import Any, Dict, Union

from equia.units import Units
from equia.models import StatusInput, StatusResult, CloudPointCalculationInput, CloudPointCalculationResult, \
    FlashCalculationInput, FlashCalculationResult, \
    BatchFlashCalculationInput, BatchFlashCalculationResult, \
    PhasediagramFixedTemperaturePressureCalculationInput, PhasediagramFixedTemperaturePressureCalculationResult, \
    FluidAddInput, FluidAddResult, FluidGetInput, FluidGetResult, FluidDeleteInput, FluidDeleteResult, \
    SlePointCalculationInput, SlePointCalculationResult, \
    EosPropertiesTPnCalculationInput, EosPropertiesTPnCalculationResult, \
    ProblemDetails \

class EquiaClient:
    """Class for making the calling to Equia API easy.
    
    Attributes
    ----------
    __base_url : str
        Base URL for the API. Includes the server address and the calculation endpoint.
    __access_key : str
        Access key for the API. This is used to authenticate the user.
    __session : aiohttp.ClientSession
        Session for making the requests to the API. This is used to manage the connection and the requests.
    """

    def __init__(self, base_url: str, access_key: str):
        self.__base_url = "{}/publicapi/".format(base_url)
        self.__access_key = access_key
        self.__session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    @classmethod
    def from_api_access(cls, api_access) -> "EquiaClient":
        """Create an `EquiaClient` instance from an `ApiAccess` object."""
        return cls(api_access.url, api_access.access_key)
    
    async def cleanup(self):
        """Close session"""
        await self.__session.close()

    def __append_body(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Method that appends access_key to the body of the request"""
        user = {
            "accesskey": self.__access_key,
        }
        return {**body, **user}

    async def __post_async(self, endpoint: str, json_body: Dict[str, Any], from_dict) -> Union[ProblemDetails, Any]:
        """Prepare the URL and the body and makes the POST request to the API"""
        url = "{}{endpoint}".format(self.__base_url, endpoint=endpoint)
        json_body = self.__append_body(json_body)
        try:
            async with self.__session.post(url, json=json_body) as resp:
                response = await resp.json()
                if resp.status == 200:
                    return from_dict(response)
                else:
                    return ProblemDetails.from_dict(response)
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))
            return ProblemDetails.from_dict(e)

    async def call_status_get_async(
        self,
        body: StatusInput,
    ) -> Union[ProblemDetails, StatusResult]: 
        """Return status of the web server."""
        return await self.__post_async("Status/GetStatus", body.to_dict(), StatusResult.from_dict)

    async def call_fluid_get_async(
        self,
        body: FluidGetInput,
    ) -> Union[ProblemDetails, FluidGetResult]: 
        """Return fluid with given id."""  
        return await self.__post_async("Fluids/GetFluid", body.to_dict(), FluidGetResult.from_dict)

    async def call_fluid_add_async(
        self,
        body: FluidAddInput,
    ) -> Union[ProblemDetails, FluidAddResult]: 
        """Add given fluid to web server and return fluid id."""  
        return await self.__post_async("Fluids/AddFluid", body.to_dict(), FluidAddResult.from_dict)

    async def call_fluid_delete_async(
        self,
        body: FluidDeleteInput,
    ) -> Union[ProblemDetails, FluidDeleteResult]: 
        """Delete given fluid on the web server."""  
        return await self.__post_async("Fluids/DeleteFluid", body.to_dict(), FluidDeleteResult.from_dict)

    # region: Flash calculations
    async def call_flash_async(
        self,
        body: FlashCalculationInput,
    ) -> Union[ProblemDetails, FlashCalculationResult]:
        """Perform flash calculation."""
        return await self.__post_async(f"Calculations/Flash/{body.flashtype}", body.to_dict(), FlashCalculationResult.from_dict)

    async def call_batchflash_async(
        self,
        body: BatchFlashCalculationInput,
    ) -> Union[ProblemDetails, BatchFlashCalculationResult]:
        """Perform batch flash calculation."""
        return await self.__post_async(f"Calculations/BatchFlash/{body.flashtype}", body.to_dict(), BatchFlashCalculationResult.from_dict)

    async def call_cloud_point_async(
        self,
        body: CloudPointCalculationInput,
    ) -> Union[ProblemDetails, CloudPointCalculationResult]:
        """Perform cloud point calculation."""
        return await self.__post_async(f"Calculations/CloudPoint/{body.pointtype}", body.to_dict(), CloudPointCalculationResult.from_dict)

    async def call_sle_point_async(
        self,
        body: SlePointCalculationInput,
    ) -> Union[ProblemDetails, SlePointCalculationResult]:
        """Perform SLE point calculation."""
        return await self.__post_async(f"Calculations/Sle/Point/{body.pointtype}", body.to_dict(), SlePointCalculationResult.from_dict)

    async def call_phasediagram_standard_async(
        self,
        body: PhasediagramFixedTemperaturePressureCalculationInput,
    ) -> Union[ProblemDetails, PhasediagramFixedTemperaturePressureCalculationResult]:
        """Perform Phasediagram standard calculation."""
        return await self.__post_async(f"Calculations/Phasediagram/FixedComposition", body.to_dict(), PhasediagramFixedTemperaturePressureCalculationResult.from_dict)

    async def call_eospropertiestpn_async(
        self,
        body: EosPropertiesTPnCalculationInput,
    ) -> Union[ProblemDetails, EosPropertiesTPnCalculationResult]:
        """Perform Eos property TPn calculation."""
        return await self.__post_async("Calculations/Properties/EosTPn", body.to_dict(), EosPropertiesTPnCalculationResult.from_dict)
    # endregion
    
    # region: Input getters
    def get_status_input(self) -> StatusInput:
        """Returns status argument filled with standard input."""
        return StatusInput(access_key=self.__access_key)

    def get_flash_input(self) -> FlashCalculationInput:
        """Returns flash argument filled with standard input."""
        return FlashCalculationInput(access_key=self.__access_key, units=self.__get_units(), components=[], fluidid="", flashtype="FixedTemperaturePressure")

    def get_batchflash_input(self) -> BatchFlashCalculationInput:
        """Returns batch flash argument filled with standard input."""
        return BatchFlashCalculationInput(access_key=self.__access_key, units=self.__get_units(), points=[], fluidid="", flashtype="FixedTemperaturePressure")

    def get_cloud_point_input(self) -> CloudPointCalculationInput:
        """Returns cloud point argument filled with standard input."""
        return CloudPointCalculationInput(access_key=self.__access_key, units=self.__get_units(), components=[], fluidid="", pointtype="FixedTemperature")

    def get_eospropertiestpn_input(self) -> EosPropertiesTPnCalculationInput:
        """Returns Eos property TPN argument filled with standard input."""
        return EosPropertiesTPnCalculationInput(access_key=self.__access_key, units=self.__get_units(), components=[], fluidid="", volumetype="Auto")

    def get_sle_point_input(self) -> SlePointCalculationInput:
        """Returns SLE point argument filled with standard input."""
        return SlePointCalculationInput(access_key=self.__access_key, units=self.__get_units(), components=[], fluidid="", pointtype="FixedPressure")

    def get_phasediagram_standard_input(self) -> PhasediagramFixedTemperaturePressureCalculationInput:
        """Returns phase diagram standard argument filled with standard input."""
        return PhasediagramFixedTemperaturePressureCalculationInput(access_key=self.__access_key, units=self.__get_units(), components=[], fluidid="")

    def get_fluid_get_input(self) -> FluidGetInput:
        """Returns request fluid argument filled with standard input."""
        return FluidGetInput(access_key=self.__access_key)

    def get_fluid_add_input(self) -> FluidAddInput:
        """Returns new fluid argument filled with standard input."""
        return FluidAddInput(access_key=self.__access_key)

    def get_fluid_delete_input(self) -> FluidDeleteInput:
        """Returns new fluid argument filled with standard input."""
        return FluidDeleteInput(access_key=self.__access_key)
    # endregion
    
    # region: Unit getter
    def __get_units(self) -> str:
        """Returns units string filled with standard units."""
        units = Units()
        return str(units)
