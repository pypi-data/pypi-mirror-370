import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerServer
from ablelabs.neon.common.notable.nanophilia.enums import (
    Axis,
    AxisDO,
    DioPDO,
    DioInput,
    RunStatus,
)
from ablelabs.neon.common.notable.nanophilia.structs import Location, Speed, FlowRate


class RobotRouter(MessengerServer):
    # robot
    async def robot_wait_boot(self):
        pass

    async def robot_shutdown(self):
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

    async def robot_get_dio_input(self) -> dict[DioInput, bool]:
        pass

    async def robot_get_environment(self) -> dict[str, float]:
        pass

    async def robot_get_run_status(self) -> RunStatus:
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

    async def robot_initialize(self):
        pass

    async def robot_delay(self, sec: float):
        pass

    # ffu
    async def robot_get_ffu(self) -> dict:
        pass

    async def robot_set_ffu(self, on: bool, rpm: float = None):
        pass

    async def robot_set_ffu_alarm_clear(self):
        pass

    # cold plate
    async def robot_get_coldplate_temperature(self) -> float:
        pass

    async def robot_set_coldplate_temperature(self, on: bool, value: float = None):
        pass

    # get
    async def get_pipette_infos(self) -> dict[int, dict]:
        pass

    async def get_tip_infos(self) -> dict[int, dict]:
        pass

    async def get_deck_module_infos(self) -> dict[int, dict]:
        pass

    async def get_labware_infos(self) -> dict[int, dict]:
        pass

    async def get_setup_data(self) -> dict:
        pass

    async def get_region_dataset(self) -> dict:
        pass

    async def get_pipette_dataset(self) -> dict:
        pass

    async def get_tip_dataset(self) -> dict:
        pass

    async def get_deck_module_dataset(self) -> dict:
        pass

    async def get_labware_dataset(self) -> dict:
        pass

    async def get_region_json(self) -> dict:
        pass

    async def get_pipette_json(self) -> dict:
        pass

    async def get_tip_json(self) -> dict:
        pass

    async def get_deck_module_json(self) -> dict:
        pass

    async def get_labware_json(self) -> dict:
        pass

    async def get_setup_data_toml(self) -> str:
        pass

    async def get_driver_param_toml(self) -> str:
        pass

    # set
    async def set_pipettes(self, value: dict[int, str | None]):
        pass

    async def set_tips(self, value: dict[int, str | None]):
        pass

    async def set_deck_modules(self, value: dict[int, str | None]):
        pass

    async def set_labwares(self, value: dict[int, str | None]):
        pass

    async def set_update_setup_data(self, value: dict, save: bool):
        pass

    async def set_update_pipette_attrs(self, value: dict[int, dict]):
        pass

    # motion(pipette)
    async def motion_initialize(self):
        pass

    async def motion_move_z_up(self):
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

    async def motion_ready_plunger(
        self,
        pipette_number: int,
        flow_rate: FlowRate = None,
    ):
        pass

    async def motion_blow_out(
        self,
        pipette_number: int,
        flow_rate: FlowRate = None,
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

    # deck_module.washer_dryer
    async def deck_module_washer_dryer_off_do(self):
        pass

    async def deck_module_washer_dryer_initialize(self):
        pass

    async def deck_module_washer_dryer_move_to_ready(self):
        pass

    async def deck_module_washer_dryer_move_to_washing(self):
        pass

    async def deck_module_washer_dryer_move_to(
        self,
        column: int,
        offset: tuple[float, float, float] = (0, 0, 0),
    ):
        pass

    async def deck_module_washer_dryer_prime(self, sec: float):
        pass

    async def deck_module_washer_dryer_recovery(self, sec: float):
        pass

    async def deck_module_washer_dryer_suction(
        self,
        columns: list[int],
        depth: float,
        z_speed: Speed = None,
        delay_sec: float = 0,
    ):
        pass

    async def deck_module_washer_dryer_dispense(
        self,
        columns: list[int],
        volume: float,
    ):
        pass

    async def deck_module_washer_dryer_wash_needle(
        self,
        depth: float,
        delay_sec: float,
    ):
        pass

    async def deck_module_washer_dryer_wash_tube(
        self,
        cycle: int,
        suction_sec: float,
        dispense_sec: float,
    ):
        pass

    async def deck_module_washer_dryer_dry(self, sec: float):
        pass

    # deck_module.magnetic_shaker
    async def deck_module_magnetic_shaker_initialize(self):
        pass

    async def deck_module_magnetic_shaker_move_to_ready(self):
        pass

    async def deck_module_magnetic_shaker_shake(self, rpm: int, acceleration_sec: int):
        pass

    async def deck_module_magnetic_shaker_shake_off(self):
        pass

    async def deck_module_magnetic_shaker_magnet(self, on: bool):
        pass

    # deck_module.shaker
    async def deck_module_shaker_initialize(self):
        pass

    async def deck_module_shaker_move_to_ready(self):
        pass

    async def deck_module_shaker_shake(self, rpm: int, acceleration_sec: int):
        pass

    async def deck_module_shaker_shake_off(self):
        pass

    # axis
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
