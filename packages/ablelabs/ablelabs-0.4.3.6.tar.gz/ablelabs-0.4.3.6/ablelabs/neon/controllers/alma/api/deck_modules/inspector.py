import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.common.alma.structs import LCRParam


class InspectorAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.deck_module_inspector_set_lcr_param)
    async def set_lcr_param(self, value: LCRParam):
        pass

    @run_server_func(RobotRouter.deck_module_inspector_scan)
    async def scan(self) -> dict[int, float]:
        pass

    @run_server_func(RobotRouter.deck_module_inspector_prepare_scan)
    async def prepare_scan(self):
        pass

    @run_server_func(RobotRouter.deck_module_inspector_complete_scan)
    async def complete_scan(self):
        pass

    @run_server_func(RobotRouter.deck_module_inspector_set_switch_on)
    async def set_switch_on(self, channel: int):
        pass

    @run_server_func(RobotRouter.deck_module_inspector_set_switch_off)
    async def set_switch_off(self):
        pass

    @run_server_func(RobotRouter.deck_module_inspector_get_lcr_value)
    async def get_lcr_value(self) -> float:
        pass
