import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.nanophilia.api.robot_router import RobotRouter
from ablelabs.neon.common.notable.nanophilia.structs import Speed


class WasherDryerAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.deck_module_washer_dryer_off_do)
    async def off_do(self):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_initialize)
    async def initialize(self):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_move_to_ready)
    async def move_to_ready(self):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_move_to_washing)
    async def move_to_washing(self):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_move_to)
    async def move_to(
        self,
        column: int,
        offset: tuple[float, float, float] = (0, 0, 0),
    ):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_prime)
    async def prime(self, sec: float):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_recovery)
    async def recovery(self, sec: float):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_suction)
    async def suction(
        self,
        columns: list[int],
        depth: float,
        z_speed: Speed = None,
        delay_sec: float = 0,
    ):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_dispense)
    async def dispense(
        self,
        columns: list[int],
        volume: float,
    ):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_wash_needle)
    async def wash_needle(
        self,
        depth: float,
        delay_sec: float,
    ):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_wash_tube)
    async def wash_tube(
        self,
        cycle: int,
        suction_sec: float,
        dispense_sec: float,
    ):
        pass

    @run_server_func(RobotRouter.deck_module_washer_dryer_dry)
    async def dry(self, sec: float):
        pass
