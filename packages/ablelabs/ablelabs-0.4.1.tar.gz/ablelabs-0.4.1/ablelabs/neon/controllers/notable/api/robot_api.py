from loguru import logger
from typing import Literal

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.api.set_api import SetAPI
from ablelabs.neon.controllers.notable.api.get_api import GetAPI
from ablelabs.neon.controllers.notable.api.motion_api import MotionAPI
from ablelabs.neon.controllers.notable.api.axis_api import AxisAPI
from ablelabs.neon.common.notable.enums import RunStatus


class RobotAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient = None) -> None:
        if tcp_client == None:
            tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)
        super().__init__(tcp_client)
        self._set_api = SetAPI(tcp_client=tcp_client)
        self._get_api = GetAPI(tcp_client=tcp_client)
        self._motion_api = MotionAPI(tcp_client=tcp_client)
        self._axis_api = AxisAPI(tcp_client=tcp_client)

    @property
    def set(self):
        return self._set_api

    @property
    def get(self):
        return self._get_api

    @property
    def motion(self):
        return self._motion_api

    @property
    def axis(self):
        return self._axis_api

    async def connect(self, ip, port):
        await self._tcp_client.connect(ip=ip, port=port)

    @run_server_func(RobotRouter.robot_wait_boot)
    async def wait_boot(self):
        pass

    @run_server_func(RobotRouter.robot_stop)
    async def stop(self):
        pass

    @run_server_func(RobotRouter.robot_clear_error)
    async def clear_error(self):
        pass

    @run_server_func(RobotRouter.robot_pause)
    async def pause(self):
        pass

    @run_server_func(RobotRouter.robot_resume)
    async def resume(self):
        pass

    @run_server_func(RobotRouter.robot_is_connected)
    async def is_connected(self) -> dict[Literal["dio", "motor"], bool]:
        pass

    @run_server_func(RobotRouter.robot_get_run_status)
    async def get_run_status(self) -> RunStatus:
        pass

    @run_server_func(RobotRouter.robot_set_run_status)
    async def set_run_status(self, value: RunStatus):
        pass
