from typing import Any

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerServer
from ablelabs.neon.common.suitable.enums import Axis, RunStatus, PipetteCalibrationType
from ablelabs.neon.common.suitable.structs import Location, Speed, FlowRate


class RobotRouter(MessengerServer):
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

    async def robot_is_connected(self):
        pass

    async def robot_get_environment(self):
        pass

    async def robot_get_run_status(self):
        pass

    async def robot_get_changed_robot_status(self):
        pass

    async def robot_set_run_status(self, value: RunStatus):
        pass

    async def robot_set_progress_rate(self, value: float):
        pass

    async def robot_set_interlock(self, value: bool):
        pass

    # get api
    async def get_setup_data(self) -> dict:
        pass

    # set api
    async def set_pipettes(self, value: dict[int, str | None]):
        pass

    async def set_tips(self, value: dict[int, str | None]):
        pass

    async def set_labwares(self, value: dict[int, str | None]):
        pass

    async def set_update_pipette_attrs(self, value: dict[int, dict]):
        pass

    async def set_pipette_calibrations(self, value: dict[int, PipetteCalibrationType]):
        pass

    # state api
    async def state_get_current_motion(self):
        pass

    async def state_get_estimated_time(self):
        pass

    # time api
    async def time_initialize(self):
        pass

    async def time_delay(self, sec: float):
        pass

    async def time_move_to_ready(self):
        pass

    async def time_move_to(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    async def time_pick_up_tip(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    async def time_drop_tip(
        self,
        pipette_number: list[int],
        location: Location,
    ):
        pass

    async def time_rise_tip(
        self,
        pipette_number: list[int],
        height_offset: float | list[float],
        z_speed: Speed | list[Speed],
    ):
        pass

    async def time_aspirate(
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

    async def time_dispense(
        self,
        pipette_number: list[int],
        volume: float | list[float],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        rise_tip_height_offset: float = None,
        rise_tip_speed: Speed = Speed.from_mm(10),
    ):
        pass

    async def time_mix(
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

    async def time_blow_out(
        self,
        pipette_number: list[int],
        flow_rate: FlowRate | list[FlowRate] = None,
    ):
        pass

    # motion api
    async def motion_initialize(self):
        pass

    async def motion_home_x(self):
        pass

    async def motion_home_y(self):
        pass

    async def motion_home_z(self):
        pass

    async def motion_home_p(self):
        pass

    async def motion_delay(self, sec: float):
        pass

    async def motion_move_to_ready(self):
        pass

    async def motion_move_to(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_pick_up_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_drop_tip(
        self,
        pipette_number: list[int],
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_rise_tip(
        self,
        pipette_number: list[int],
        height_offset: float | list[float],
        z_speed: Speed | list[Speed],
        optimize: bool = False,
    ):
        pass

    async def motion_aspirate(
        self,
        pipette_number: list[int],
        volume: float | list[list[float]],
        location: Location = None,
        flow_rate: FlowRate | list[FlowRate] = None,
        rise_tip_height_offset: float = None,
        pre_wet_count: int = 0,
        optimize: bool = False,
    ):
        pass

    async def motion_dispense(
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

    async def motion_mix(
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

    async def motion_blow_out(
        self,
        pipette_number: list[int],
        flow_rate: FlowRate | list[FlowRate] = None,
    ):
        pass

    # axis api
    async def axis_get_position(self, axis: Axis, floor_digit: int = 1):
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
