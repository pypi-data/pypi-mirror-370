import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.nanophilia.api.robot_router import RobotRouter


class MagneticShakerAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.deck_module_magnetic_shaker_initialize)
    async def initialize(self):
        pass

    @run_server_func(RobotRouter.deck_module_magnetic_shaker_move_to_ready)
    async def move_to_ready(self):
        pass

    @run_server_func(RobotRouter.deck_module_magnetic_shaker_shake)
    async def shake(self, rpm: int, acceleration_sec: int):
        pass

    @run_server_func(RobotRouter.deck_module_magnetic_shaker_shake_off)
    async def shake_off(self):
        pass

    @run_server_func(RobotRouter.deck_module_magnetic_shaker_magnet)
    async def magnet(self, on: bool):
        pass
