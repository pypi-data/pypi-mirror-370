import asyncio
from loguru import logger
import cv2

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.api.robot_api import RobotAPI as BaseRobotAPI
from ablelabs.neon.controllers.notable.kribb.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.kribb.api.set_api import SetAPI
from ablelabs.neon.controllers.notable.kribb.api.motion_api import MotionAPI
from ablelabs.neon.controllers.notable.kribb.api.optic_api import OpticAPI
from ablelabs.neon.common.notable.structs import Location


class RobotAPI(BaseRobotAPI):
    def __init__(self) -> None:
        tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)
        super().__init__(tcp_client)
        self._set_api = SetAPI(tcp_client=tcp_client)
        self._motion_api = MotionAPI(tcp_client=tcp_client)
        self._optic_api = OpticAPI(tcp_client=tcp_client)

    @property
    def set(self):
        return self._set_api

    @property
    def motion(self):
        return self._motion_api

    @property
    def optic(self):
        return self._optic_api

    @run_server_func(RobotRouter.robot_scan_displacement_sensor)
    async def scan_displacement_sensor(
        self,
        pipette_number: int,
        location: Location,
        padding: tuple[float, float],
        scan_count: tuple[float, float],
    ) -> tuple[list[float], list[float], list[list[float]], float, float, cv2.Mat]:
        pass

    @run_server_func(RobotRouter.robot_move_to_interpolated_z)
    async def move_to_interpolated_z(
        self,
        pipette_number: int,
        location: Location,
        x: float,
        y: float,
    ):
        pass
