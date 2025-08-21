from typing import Any
import cv2

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerServer
from ablelabs.neon.common.notable.enums import Axis
from ablelabs.neon.common.notable.structs import Location, Speed, FlowRate
from ablelabs.neon.common.notable.kribb.structs import LabelInfo


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

    async def robot_scan_displacement_sensor(
        self,
        pipette_number: int,
        location: Location,
        padding: tuple[float, float],
        scan_count: tuple[float, float],
    ):
        pass

    async def robot_move_to_interpolated_z(
        self,
        pipette_number: int,
        location: Location,
        x: float,
        y: float,
    ):
        pass

    # set api
    async def set_pipettes(self, value: dict[int, str | None]):
        pass

    async def set_tips(self, value: dict[int, str | None]):
        pass

    async def set_deck_modules(self, value: dict[int, str | None]):
        pass

    async def set_labwares(self, value: dict[int, str | None]):
        pass

    async def set_update_pipette_attrs(self, value: dict[int, dict]):
        pass

    async def set_update_setup_data(self, value: dict, save: bool):
        pass

    async def set_camera(self, pipette_number: int):
        pass

    # get api
    async def get_pipette_infos(self):
        pass

    async def get_tip_infos(self):
        pass

    async def get_deck_module_infos(self):
        pass

    async def get_labware_infos(self):
        pass

    async def get_setup_data(self):
        pass

    # motion api
    async def motion_initialize(self):
        pass

    async def motion_delay(self, sec: float):
        pass

    async def motion_move_to_ready(self):
        pass

    async def motion_move_to(
        self,
        pipette_number: int,
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_move_to_camera(
        self,
        pipette_number: int,
        location: Location,
    ):
        pass

    async def motion_move_to_displacement_sensor(
        self,
        pipette_number: int,
        location: Location,
    ):
        pass

    async def motion_pick_up_tip(
        self,
        pipette_number: int,
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_drop_tip(
        self,
        pipette_number: int,
        location: Location,
        optimize: bool = False,
    ):
        pass

    async def motion_rise_tip(
        self,
        pipette_number: int,
        height_offset: float,
        z_speed: Speed,
    ):
        pass

    async def motion_aspirate(
        self,
        pipette_number: int,
        volume: float,
        location: Location = None,
        flow_rate: FlowRate = None,
        optimize: bool = False,
    ):
        pass

    async def motion_dispense(
        self,
        pipette_number: int,
        volume: float,
        location: Location = None,
        flow_rate: FlowRate = None,
        optimize: bool = False,
    ):
        pass

    async def motion_mix(
        self,
        pipette_number: int,
        volume: float,
        iteration: int,
        location: Location = None,
        flow_rate: FlowRate = None,
        delay: float = 0.0,
        optimize: bool = False,
    ):
        pass

    async def motion_blow_out(
        self,
        pipette_number: int,
        flow_rate: FlowRate = None,
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

    # optic api
    async def optic_set_camera_live(self, on: bool):
        pass

    async def optic_camera_capture(self, resize_ratio: float = None):
        pass

    async def optic_camera_show(
        self,
        winname: str,
        resize_ratio: float = 0.5,
    ):
        pass

    async def optic_set_led_brightness(self, value: int):
        pass

    async def optic_set_led_on_off(self, on: bool):
        pass

    async def optic_set_displacement_zero(self):
        pass

    async def optic_get_displacement_value(self):
        pass

    async def optic_detect_colony(
        self,
        image: cv2.Mat = None,
        resize_ratio: float = 0.5,
        padding: tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5),
        rect_refer: cv2.typing.Rect = (8, 8, 83, 83),
        rect_tolerance: int = 5,
        vignette_size: int = 30,
        binary_thresh: int = 170,
        crop_border_thresh: int = 30,
        return_process_images: bool = False,
        font_scale: float = 0.7,
    ):
        pass

    async def optic_group_colony(
        self,
        crop_info: tuple[int, int, int, int],
        label_infos: list[LabelInfo],
        image: cv2.Mat = None,
        pick_count: int = 1,
        resize_ratio: float = 0.5,
        padding: tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.5),
        initial_dist: float = 60,
        row: int = 8,
        column: int = 12,
    ):
        pass
