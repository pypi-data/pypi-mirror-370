from typing import Callable, Coroutine, Literal

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerServer
from ablelabs.neon.common.alma.enums import (
    DioInput,
    Axis,
    RunStatus,
    LocationType,
    ZGripper,
)
from ablelabs.neon.common.alma.structs import (
    Location,
    LCRParam,
    HeaterData,
    State,
    Speed,
)


class RobotRouter(MessengerServer):
    # robot
    async def robot_wait_boot(self):
        pass

    async def robot_stop(self):
        pass

    async def robot_clear_error(self):
        pass

    async def robot_pause(self):
        pass

    async def robot_resume(self):
        pass

    async def robot_is_connected(self) -> dict[str, bool]:
        pass

    async def robot_get_environment(self) -> dict[str, float]:
        pass

    async def robot_get_run_status(self) -> RunStatus:
        pass

    async def robot_get_dio_input(self) -> dict[DioInput, bool]:
        pass

    async def robot_get_last_state(self) -> State:
        pass

    async def robot_get_changed_robot_status(self) -> dict:
        pass

    async def robot_set_interlock(self, value: bool):
        pass

    async def robot_set_led_lamp(self, on: bool):
        pass

    async def robot_set_run_status(self, value: RunStatus):
        pass

    async def robot_set_progress_rate(self, value: float):
        pass

    async def robot_initialize(self, recovery: bool):
        pass

    async def robot_initialize_teaching(self):
        pass

    async def robot_calibrate_lcr_meter(self):
        pass

    # get
    async def get_setup_data(self) -> dict:
        pass

    # set
    async def set_update_setup_data(self, value: dict, save: bool):
        pass

    async def set_update_pipette_attrs(self, value: dict[int, dict]):
        pass

    # time
    async def time_initialize(self) -> float:
        pass

    async def time_calibrate_lcr_meter(self) -> float:
        pass

    # time.upper_module
    async def time_upper_module_move_z_up(self) -> float:
        pass

    async def time_upper_module_move_to_ready(self) -> float:
        pass

    # time.upper_module.gripper
    async def time_upper_module_gripper_move_block_to_inspector(
        self,
        push: bool,
    ) -> float:
        pass

    async def time_upper_module_gripper_move_block_to_holder(self) -> float:
        pass

    async def time_upper_module_gripper_open_lid(
        self,
        chip_holder_number: int,
        lid_holder_number: int,
    ) -> float:
        pass

    async def time_upper_module_gripper_close_lid(
        self,
        lid_holder_number: int,
        chip_holder_number: int,
    ) -> float:
        pass

    async def time_upper_module_gripper_move_labware(
        self,
        from_location: Location,
        to_location: Location,
        push: bool = False,
    ) -> float:
        pass

    async def time_upper_module_gripper_move_lid(
        self,
        from_location: Location,
        to_location: Location,
    ) -> float:
        pass

    async def time_upper_module_gripper_pick_labware(self, location: Location) -> float:
        pass

    async def time_upper_module_gripper_place_labware(
        self,
        location: Location,
        push: bool = False,
    ) -> float:
        pass

    async def time_upper_module_gripper_pick_lid(self, location: Location) -> float:
        pass

    async def time_upper_module_gripper_place_lid(self, location: Location) -> float:
        pass

    async def time_upper_module_gripper_move_to(
        self,
        location: Location,
        z_gripper: ZGripper,
        slow_z_offset: float = 0,
    ) -> float:
        pass

    # time.upper_module.pipette
    async def time_upper_module_pipette_pick_up_tip(
        self, well: str, optimize: bool = True
    ) -> float:
        pass

    async def time_upper_module_pipette_drop_tip(
        self,
        location_type: LocationType,
        well: str,
        optimize: bool = True,
    ) -> float:
        pass

    async def time_upper_module_pipette_move_to(
        self,
        location: Location,
        z_speed: Speed = None,
        optimize: bool = False,
    ) -> float:
        pass

    async def time_upper_module_pipette_ready_plunger(
        self, flow_rate: float = None
    ) -> float:
        pass

    async def time_upper_module_pipette_blow_out(
        self, flow_rate: float = None
    ) -> float:
        pass

    async def time_upper_module_pipette_aspirate(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        flow_rate: float = None,
        height_offset: float = 0,
    ) -> float:
        pass

    async def time_upper_module_pipette_dispense(
        self,
        volume: float,
        flow_rate: float = None,
        height_offset: float = 0,
    ) -> float:
        pass

    async def time_upper_module_pipette_mix(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        iteration: int,
        flow_rate: float = None,
        delay: float = 0.0,
        height_offset: float = 0,
    ) -> float:
        pass

    # upper_module
    async def upper_module_move_z_up(self):
        pass

    async def upper_module_move_to_ready(self):
        pass

    # upper_module.gripper
    async def upper_module_gripper_move_block_to_inspector(self, push: bool):
        pass

    async def upper_module_gripper_move_block_to_holder(self):
        pass

    async def upper_module_gripper_open_lid(
        self,
        chip_holder_number: int,
        lid_holder_number: int,
    ):
        pass

    async def upper_module_gripper_close_lid(
        self,
        lid_holder_number: int,
        chip_holder_number: int,
    ):
        pass

    async def upper_module_gripper_move_labware(
        self,
        from_location: Location,
        to_location: Location,
        push: bool = False,
    ):
        pass

    async def upper_module_gripper_move_lid(
        self,
        from_location: Location,
        to_location: Location,
    ):
        pass

    async def upper_module_gripper_pick_labware(self, location: Location):
        pass

    async def upper_module_gripper_place_labware(
        self,
        location: Location,
        push: bool = False,
    ):
        pass

    async def upper_module_gripper_pick_lid(self, location: Location):
        pass

    async def upper_module_gripper_place_lid(self, location: Location):
        pass

    async def upper_module_gripper_move_to(
        self,
        location: Location,
        z_gripper: ZGripper,
        task_after_z_up: Callable[[], Coroutine] = None,
        slow_z_offset: float = 0,
    ):
        pass

    # upper_module.pipette
    async def upper_module_pipette_pick_up_tip(self, well: str, optimize: bool = True):
        pass

    async def upper_module_pipette_drop_tip(
        self,
        location_type: LocationType,
        well: str,
        optimize: bool = True,
    ):
        pass

    async def upper_module_pipette_move_to(
        self,
        location: Location,
        task_after_z_up: Callable[[], Coroutine] = None,
        z_speed: Speed = None,
        optimize: bool = False,
    ):
        pass

    async def upper_module_pipette_ready_plunger(self, flow_rate: float = None):
        pass

    async def upper_module_pipette_blow_out(self, flow_rate: float = None):
        pass

    async def upper_module_pipette_aspirate(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        flow_rate: float = None,
        height_offset: float = 0,
    ):
        pass

    async def upper_module_pipette_dispense(
        self,
        volume: float,
        flow_rate: float = None,
        height_offset: float = 0,
    ):
        pass

    async def upper_module_pipette_mix(
        self,
        volume: float | list[float],  # list for multi-dispense calibration
        iteration: int,
        flow_rate: float = None,
        delay: float = 0.0,
        height_offset: float = 0,
    ):
        pass

    # deck_module.inspector
    async def deck_module_inspector_set_lcr_param(self, value: LCRParam):
        pass

    async def deck_module_inspector_scan(self) -> dict[int, float]:
        pass

    async def deck_module_inspector_prepare_scan(self):
        pass

    async def deck_module_inspector_complete_scan(self):
        pass

    async def deck_module_inspector_set_switch_on(self, channel: int):
        pass

    async def deck_module_inspector_set_switch_off(self):
        pass

    async def deck_module_inspector_get_lcr_value(self) -> float:
        pass

    # deck_module.heater
    async def deck_module_heater_get_heater_on(self) -> dict[int, bool]:
        pass

    async def deck_module_heater_get_temperature(self) -> dict[int, float]:
        pass

    async def deck_module_heater_set_environment_temperature(self, value: float):
        pass

    async def deck_module_heater_set_temperature(self, values: dict[int, HeaterData]):
        pass

    # axis
    async def axis_get_position(self, axis: Axis, floor_digit: int = 1) -> float:
        pass

    async def axis_set_speed(self, axis: Axis, value: float):
        pass

    async def axis_set_accel(self, axis: Axis, value: float):
        pass

    async def axis_set_decel(self, axis: Axis, value: float):
        pass

    async def axis_enable(self, axis: Axis):
        pass

    async def axis_disable(self, axis: Axis):
        pass

    async def axis_stop(self, axis: Axis):
        pass

    async def axis_home(self, axis: Axis):
        pass

    async def axis_jog(self, axis: Axis, value: float):
        pass

    async def axis_step(self, axis: Axis, value: float):
        pass

    async def axis_move(self, axis: Axis, value: float):
        pass

    async def axis_wait_home_done(self, axis: Axis):
        pass

    async def axis_wait_move_done(self, axis: Axis):
        pass
