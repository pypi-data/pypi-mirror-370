from typing import Callable, Coroutine

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.common.alma.enums import ZGripper
from ablelabs.neon.common.alma.structs import Location


class GripperAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.upper_module_gripper_move_block_to_inspector)
    async def move_block_to_inspector(self, push: bool):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_move_block_to_holder)
    async def move_block_to_holder(self):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_open_lid)
    async def open_lid(self, chip_holder_number: int, lid_holder_number: int):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_close_lid)
    async def close_lid(self, lid_holder_number: int, chip_holder_number: int):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_move_labware)
    async def move_labware(
        self,
        from_location: Location,
        to_location: Location,
        push: bool = False,
    ):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_move_lid)
    async def move_lid(self, from_location: Location, to_location: Location):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_pick_labware)
    async def pick_labware(self, location: Location):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_place_labware)
    async def place_labware(self, location: Location, push: bool = False):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_pick_lid)
    async def pick_lid(self, location: Location):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_place_lid)
    async def place_lid(self, location: Location):
        pass

    @run_server_func(RobotRouter.upper_module_gripper_move_to)
    async def move_to(
        self,
        location: Location,
        z_gripper: ZGripper,
        task_after_z_up: Callable[[], Coroutine] = None,
        slow_z_offset: float = 0,
    ):
        pass
