import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter
from ablelabs.neon.common.suitable.structs import Location, Speed, FlowRate


class MotionAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.motion_initialize)
    async def initialize(self):
        pass

    @run_server_func(RobotRouter.motion_home_x)
    async def home_x(self):
        pass

    @run_server_func(RobotRouter.motion_home_y)
    async def home_y(self):
        pass

    @run_server_func(RobotRouter.motion_home_z)
    async def home_z(self):
        pass

    @run_server_func(RobotRouter.motion_home_p)
    async def home_p(self):
        pass

    @run_server_func(RobotRouter.motion_delay)
    async def delay(self, sec: float):
        pass

    @run_server_func(RobotRouter.motion_move_to_ready)
    async def move_to_ready(self):
        pass

    @run_server_func(RobotRouter.motion_move_to)
    async def move_to(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_pick_up_tip)
    async def pick_up_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_drop_tip)
    async def drop_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_rise_tip)
    async def rise_tip(
        self,
        pipette_number: list[int],
        height_offset: float | list[float],
        z_speed: Speed | list[Speed],
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_aspirate)
    async def aspirate(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        rise_tip_height_offset: float = None,
        pre_wet_count: int = 0,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_dispense)
    async def dispense(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        liquid_following: bool = False,
        rise_tip_height_offset: float = None,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_mix)
    async def mix(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        iteration: int,
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        delay: float = 0.0,
        liquid_following: bool = False,
        rise_tip_height_offset: float = None,
        optimize: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.motion_blow_out)
    async def blow_out(
        self,
        pipette_number: list[int],
        flow_rate: FlowRate | list[FlowRate] = None,
    ):
        pass
