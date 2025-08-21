from loguru import logger

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.kribb.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.api.set_api import SetAPI as BaseSetAPI


class SetAPI(BaseSetAPI):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.set_camera)
    async def camera(
        self,
        pipette_number: int,
    ):
        pass
