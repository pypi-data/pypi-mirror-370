from loguru import logger

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.kribb.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.api.motion_api import MotionAPI as BaseMotionAPI
from ablelabs.neon.common.notable.structs import Location


class MotionAPI(BaseMotionAPI):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.motion_move_to_camera)
    async def move_to_camera(
        self,
        pipette_number: int,
        location: Location,
    ):
        pass

    @run_server_func(RobotRouter.motion_move_to_displacement_sensor)
    async def move_to_displacement_sensor(
        self,
        pipette_number: int,
        location: Location,
    ):
        pass
