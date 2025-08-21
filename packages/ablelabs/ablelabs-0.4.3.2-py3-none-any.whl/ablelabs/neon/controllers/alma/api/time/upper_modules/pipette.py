from typing import Callable, Coroutine

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.common.alma.enums import LocationType
from ablelabs.neon.common.alma.structs import Location, FlowRate, Speed


class TimePipetteAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.time_upper_module_pipette_pick_up_tip)
    async def pick_up_tip(
        self,
        well: str,
        optimize: bool = True,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_drop_tip)
    async def drop_tip(
        self,
        location_type: LocationType,
        well: str,
        optimize: bool = True,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_move_to)
    async def move_to(
        self,
        location: Location,
        # task_after_z_up: Callable[[], Coroutine] = None,
        z_speed: Speed = None,
        optimize: bool = False,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_ready_plunger)
    async def ready_plunger(
        self,
        flow_rate: FlowRate = None,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_blow_out)
    async def blow_out(
        self,
        flow_rate: FlowRate = None,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_aspirate)
    async def aspirate(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        flow_rate: float = None,
        height_offset: float = 0,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_dispense)
    async def dispense(
        self,
        volume: float,
        flow_rate: float = None,
        height_offset: float = 0,
    ) -> float:
        pass

    @run_server_func(RobotRouter.time_upper_module_pipette_mix)
    async def mix(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        iteration: int,
        flow_rate: float = None,
        delay: float = 0.0,
        height_offset: float = 0,
    ) -> float:
        pass
