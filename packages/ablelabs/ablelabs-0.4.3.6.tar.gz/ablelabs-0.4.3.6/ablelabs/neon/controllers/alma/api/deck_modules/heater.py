import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.common.alma.structs import HeaterData


class HeaterAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.deck_module_heater_get_heater_on)
    async def get_heater_on(self) -> dict[int, bool]:
        pass

    @run_server_func(RobotRouter.deck_module_heater_get_temperature)
    async def get_temperature(self) -> dict[int, float]:
        pass

    @run_server_func(RobotRouter.deck_module_heater_set_environment_temperature)
    async def set_environment_temperature(self, value: float):
        pass

    @run_server_func(RobotRouter.deck_module_heater_set_temperature)
    async def set_temperature(self, values: dict[int, HeaterData]):
        pass
