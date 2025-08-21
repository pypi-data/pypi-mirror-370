import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.controllers.alma.api.time.upper_module import TimeUpperModuleAPI


class TimeAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)
        self.upper_module = TimeUpperModuleAPI(tcp_client)

    @run_server_func(RobotRouter.time_initialize)
    async def initialize(
        self,
        # recovery: bool,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_calibrate_lcr_meter)
    async def calibrate_lcr_meter(self) -> float:
        pass
