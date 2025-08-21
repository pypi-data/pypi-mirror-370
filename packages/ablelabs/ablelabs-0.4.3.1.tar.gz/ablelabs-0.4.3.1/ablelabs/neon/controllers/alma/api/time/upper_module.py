import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.controllers.alma.api.time.upper_modules.gripper import TimeGripperAPI
from ablelabs.neon.controllers.alma.api.time.upper_modules.pipette import TimePipetteAPI


class TimeUpperModuleAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)
        self.pipette = TimePipetteAPI(tcp_client)
        self.gripper = TimeGripperAPI(tcp_client)

    @run_server_func(RobotRouter.time_upper_module_move_z_up)
    async def move_z_up(self) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_move_to_ready)
    async def move_to_ready(self) -> float:
        pass
