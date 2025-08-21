import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter
from ablelabs.neon.common.suitable.enums import Axis


class AxisAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.axis_get_position)
    async def get_position(self, axis: Axis, floor_digit: int = 1):
        pass

    @run_server_func(RobotRouter.axis_set_speed)
    async def set_speed(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_set_accel)
    async def set_accel(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_set_decel)
    async def set_decel(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_enable)
    async def enable(self, axis: Axis):
        pass

    @run_server_func(RobotRouter.axis_disable)
    async def disable(self, axis: Axis):
        pass

    @run_server_func(RobotRouter.axis_stop)
    async def stop(self, axis: Axis):
        pass

    @run_server_func(RobotRouter.axis_home)
    async def home(self, axis: Axis):
        pass

    @run_server_func(RobotRouter.axis_jog)
    async def jog(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_step)
    async def step(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_move)
    async def move(self, axis: Axis, value: float):
        pass

    @run_server_func(RobotRouter.axis_wait_home_done)
    async def wait_home_done(self, axis: Axis):
        pass

    @run_server_func(RobotRouter.axis_wait_move_done)
    async def wait_move_done(self, axis: Axis):
        pass
