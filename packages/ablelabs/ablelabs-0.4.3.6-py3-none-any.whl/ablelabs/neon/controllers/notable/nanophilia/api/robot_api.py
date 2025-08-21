from loguru import logger

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.nanophilia.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.nanophilia.api.get_api import GetAPI
from ablelabs.neon.controllers.notable.nanophilia.api.set_api import SetAPI

# from ablelabs.neon.controllers.notable.nanophilia.api.time_api import TimeAPI
from ablelabs.neon.controllers.notable.nanophilia.api.motion_api import MotionAPI
from ablelabs.neon.controllers.notable.nanophilia.api.deck_module import DeckModuleAPI
from ablelabs.neon.controllers.notable.nanophilia.api.axis_api import AxisAPI
from ablelabs.neon.common.notable.nanophilia.enums import RunStatus, DioInput


class RobotAPI(MessengerClient):
    def __init__(self) -> None:
        tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)
        super().__init__(tcp_client)
        self._get_api = GetAPI(tcp_client=tcp_client)
        self._set_api = SetAPI(tcp_client=tcp_client)
        # self._time_api = TimeAPI(tcp_client=tcp_client)
        self._motion_api = MotionAPI(tcp_client=tcp_client)
        self._deck_module_api = DeckModuleAPI(tcp_client=tcp_client)
        self._axis_api = AxisAPI(tcp_client=tcp_client)

    @property
    def get(self):
        return self._get_api

    @property
    def set(self):
        return self._set_api

    # @property
    # def time(self):
    #     return self._time_api

    @property
    def motion(self):
        return self._motion_api

    @property
    def deck_module(self):
        return self._deck_module_api

    @property
    def axis(self):
        return self._axis_api

    async def connect(self, ip, port):
        await self._tcp_client.connect(ip=ip, port=port)

    @run_server_func(RobotRouter.robot_wait_boot)
    async def wait_boot(self):
        pass

    @run_server_func(RobotRouter.robot_shutdown)
    async def shutdown(self):
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
    async def is_connected(self) -> dict[str, bool]:
        pass

    @run_server_func(RobotRouter.robot_get_dio_input)
    async def get_dio_input(self) -> dict[DioInput, bool]:
        pass

    @run_server_func(RobotRouter.robot_get_environment)
    async def get_environment(self) -> dict[str, float]:
        pass

    @run_server_func(RobotRouter.robot_get_run_status)
    async def get_run_status(self) -> RunStatus:
        pass

    @run_server_func(RobotRouter.robot_get_changed_robot_status)
    async def get_changed_robot_status(self) -> dict:
        pass

    @run_server_func(RobotRouter.robot_set_interlock)
    async def set_interlock(self, value: bool):
        pass

    @run_server_func(RobotRouter.robot_set_led_lamp)
    async def set_led_lamp(self, on: bool):
        pass

    @run_server_func(RobotRouter.robot_set_run_status)
    async def set_run_status(self, value: RunStatus):
        pass

    @run_server_func(RobotRouter.robot_set_progress_rate)
    async def set_progress_rate(self, value: float):
        pass

    @run_server_func(RobotRouter.robot_initialize)
    async def initialize(self):
        pass

    @run_server_func(RobotRouter.robot_delay)
    async def delay(self, sec: float):
        pass

    # ffu
    @run_server_func(RobotRouter.robot_get_ffu)
    async def get_ffu(self) -> dict:
        pass

    @run_server_func(RobotRouter.robot_set_ffu)
    async def set_ffu(self, on: bool, rpm: float = None):
        pass

    @run_server_func(RobotRouter.robot_set_ffu_alarm_clear)
    async def set_ffu_alarm_clear(self):
        pass

    # cold plate
    @run_server_func(RobotRouter.robot_get_coldplate_temperature)
    async def get_coldplate_temperature(self) -> float:
        pass

    @run_server_func(RobotRouter.robot_set_coldplate_temperature)
    async def set_coldplate_temperature(self, on: bool, value: float = None):
        pass
