import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.nanophilia.api.robot_router import RobotRouter


class GetAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.get_pipette_infos)
    async def pipette_infos(self) -> dict[int, dict]:
        pass

    @run_server_func(RobotRouter.get_tip_infos)
    async def tip_infos(self) -> dict[int, dict]:
        pass

    @run_server_func(RobotRouter.get_deck_module_infos)
    async def deck_module_infos(self) -> dict[int, dict]:
        pass

    @run_server_func(RobotRouter.get_labware_infos)
    async def labware_infos(self) -> dict[int, dict]:
        pass

    @run_server_func(RobotRouter.get_setup_data)
    async def setup_data(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_region_dataset)
    async def region_dataset(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_pipette_dataset)
    async def pipette_dataset(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_tip_dataset)
    async def tip_dataset(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_deck_module_dataset)
    async def deck_module_dataset(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_labware_dataset)
    async def labware_dataset(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_region_json)
    async def region_json(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_pipette_json)
    async def pipette_json(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_tip_json)
    async def tip_json(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_deck_module_json)
    async def deck_module_json(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_labware_json)
    async def labware_json(self) -> dict:
        pass

    @run_server_func(RobotRouter.get_setup_data_toml)
    async def setup_data_toml(self) -> str:
        pass

    @run_server_func(RobotRouter.get_driver_param_toml)
    async def driver_param_toml(self) -> str:
        pass
