import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.api.robot_router import RobotRouter


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
