import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter
from ablelabs.neon.common.suitable.structs import Location, Speed, FlowRate


class TimeAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.time_initialize)
    async def initialize(self):
        pass

    @run_server_func(RobotRouter.time_delay)
    async def delay(self, sec: float):
        pass

    @run_server_func(RobotRouter.time_move_to_ready)
    async def move_to_ready(self):
        pass

    @run_server_func(RobotRouter.time_move_to)
    async def move_to(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    @run_server_func(RobotRouter.time_pick_up_tip)
    async def pick_up_tip(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    @run_server_func(RobotRouter.time_drop_tip)
    async def drop_tip(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    @run_server_func(RobotRouter.time_rise_tip)
    async def rise_tip(
        self,
        pipette_number: list[int],
        height_offset: float | list[float],
        z_speed: Speed | list[Speed],
    ):
        pass

    @run_server_func(RobotRouter.time_aspirate)
    async def aspirate(
        self,
        pipette_number: list[int],
        volume: (
            float | list[list[float]]
        ),  # [[p1.v1, p2.v1], [p1.v2, p2.v2], [p1.v3, p2.v3], ... ]
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        rise_tip_height_offset: float = None,
        rise_tip_speed: Speed = Speed.from_mm(10),
        pre_wet_count: int = 0,
    ):
        pass

    @run_server_func(RobotRouter.time_dispense)
    async def dispense(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        rise_tip_height_offset: float = None,
        rise_tip_speed: Speed = Speed.from_mm(10),
    ):
        pass

    @run_server_func(RobotRouter.time_mix)
    async def mix(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        iteration: int,
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        delay: float = 0.0,
        rise_tip_height_offset: float = None,
        rise_tip_speed: Speed = Speed.from_mm(10),
    ):
        pass

    @run_server_func(RobotRouter.time_blow_out)
    async def blow_out(
        self,
        pipette_number: list[int],
        flow_rate: FlowRate | list[FlowRate] = None,
    ):
        pass
