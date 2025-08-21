# python 3.10 버전

# 가상환경 설정
## python -m venv .venv
## py 3.10 -m venv .venv

# ablelabs 패키지 설치
## pip install ablelabs

# Neon.exe + resources 파일 위치 확인
## resources 폴더는 Neon.exe와 같은 폴더 또는 하위 폴더에

# subprocess.Popen으로 Neon.exe 실행

# connect -> wait_boot 순서대로 호출


import asyncio
import sys, os
from typing import Literal

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.controllers.alma.api.robot_api import RobotAPI
from ablelabs.neon.common.alma.enums import (
    LocationType,
    Axis,
    LocationReference,
    RunStatus,
    ZGripper,
    DioInput,
)
from ablelabs.neon.common.alma.structs import (
    State,
    location,
    LCRParam,
    MeasurementTimeMode,
    HeaterData,
    Speed,
)


async def main():
    import subprocess

    # for windows
    # subprocess.Popen(
    #     [
    #         r"C:\your_path\Neon.exe",
    #     ]
    # )

    # for mac dev
    subprocess.Popen(
        [
            r"/Users/sypark/Code/ABLE-Elba/.venv/bin/python",
            r"/Users/sypark/Code/ABLE-Elba/robot/src/controllers/alma/robot_router.py",
        ],
        cwd=r"/Users/sypark/Code/ABLE-Elba",
    )
    await asyncio.sleep(1)

    ip = "localhost"
    port = 1234

    # robot
    robot_api = RobotAPI()
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass
    await robot_api.wait_boot()

    await robot_api.stop()
    await robot_api.clear_error()  # stop 이후, motion 전에. / fault 후에.
    await robot_api.pause()
    await robot_api.resume()
    is_connected: dict[
        Literal[
            "motor",
            "dio",
            "heater",
            "switcher",
            "lcr_meter",
        ],
        bool,
    ] = await robot_api.is_connected()
    environment: dict[
        Literal[
            "temperature",
            "pressure",
            "humidity",
        ],
        float,
    ] = await robot_api.get_environment()
    run_status: RunStatus = await robot_api.get_run_status()
    dio_input: dict[DioInput, bool] = await robot_api.get_dio_input()
    last_state: State = await robot_api.get_last_state()

    await robot_api.set_interlock(value=False)
    await robot_api.set_led_lamp(on=True)

    await robot_api.set_run_status(value=RunStatus.INITIALIZE)
    await robot_api.initialize(recovery=True)
    await robot_api.initialize_teaching()
    await robot_api.calibrate_lcr_meter()
    await asyncio.sleep(0.5)

    async def get_changed_robot_status():
        while True:
            robot_status = await robot_api.get_changed_robot_status()
            run_status: RunStatus = robot_status["run_status"]
            is_door_open: bool = robot_status["is_door_open"]
            dio_input: dict[DioInput, bool] = robot_status["dio_input"]

    asyncio.create_task(get_changed_robot_status())

    await robot_api.set_run_status(value=RunStatus.RUN)
    await robot_api.set_progress_rate(value=5)
    await robot_api.set_run_status(value=RunStatus.DONE)

    # get
    setup_data: dict = await robot_api.get.setup_data()

    # set
    x, y, z = setup_data["teaching"]["absolute_origin"]["pipette_deck_1"]
    setup_data["teaching"]["absolute_origin"]["pipette_deck_1"] = [x + 1, y + 2, z + 3]
    setup_data["option"]["pipette"]["cal_a"] = 1.321
    await robot_api.set.update_setup_data(value=setup_data, save=True)
    setup_data_2: dict = await robot_api.get.setup_data()
    await robot_api.set.update_pipette_attrs(
        value={
            2: {
                "blow_out_volume": 20,
            }
        }
    )

    # time
    sec = 0
    sec += await robot_api.time.initialize()
    sec += await robot_api.time.calibrate_lcr_meter()
    # time.upper_module
    sec += await robot_api.time.upper_module.move_z_up()
    sec += await robot_api.time.upper_module.move_to_ready()
    # time.upper_module.gripper
    sec += await robot_api.time.upper_module.gripper.move_block_to_inspector(push=True)
    sec += await robot_api.time.upper_module.gripper.move_block_to_holder()
    sec += await robot_api.time.upper_module.gripper.open_lid(
        chip_holder_number=1,
        lid_holder_number=2,
    )
    sec += await robot_api.time.upper_module.gripper.close_lid(
        lid_holder_number=2,
        chip_holder_number=1,
    )
    sec += await robot_api.time.upper_module.gripper.move_labware(
        from_location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=1,
        ),
        to_location=location(
            location_type=LocationType.INSPECTOR,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.move_lid(
        from_location=location(
            location_type=LocationType.LID_HOLDER,
            location_number=1,
        ),
        to_location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=2,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.pick_labware(
        location=location(
            location_type=LocationType.INSPECTOR,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.place_labware(
        location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=1,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.pick_lid(
        location=location(
            location_type=LocationType.LID_HOLDER,
            location_number=1,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.place_lid(
        location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=2,
        ),
    )
    sec += await robot_api.time.upper_module.gripper.move_to(
        location=location(
            location_type=LocationType.DECK,
            location_number=1,
        ),
        z_gripper=ZGripper.UNDER_PLATE,
        slow_z_offset=5,
    )
    # time.upper_module.pipette
    sec += await robot_api.time.upper_module.pipette.pick_up_tip(
        well="a1",
    )
    sec += await robot_api.time.upper_module.pipette.drop_tip(
        location_type=LocationType.WASTE,
        # location_type=LocationType.TIP_RACK,
        well="a1",
    )
    sec += await robot_api.time.upper_module.pipette.move_to(
        location=location(
            location_type=LocationType.RESERVOIR,
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(0, 0, 1.2),
        ),
    )
    sec += await robot_api.time.upper_module.pipette.mix(
        volume=[50, 50],
        iteration=3,
        flow_rate=100,
    )
    sec += await robot_api.time.upper_module.pipette.aspirate(
        volume=[50, 50],
        flow_rate=100,
    )
    wells = ["a1", "b1"]
    for i, well in enumerate(wells):
        sec += await robot_api.time.upper_module.pipette.move_to(
            location=location(
                location_type=LocationType.CHIP_HOLDER,
                location_number=1,
                well=well,
                reference=LocationReference.BOTTOM,
            ),
        )
        sec += await robot_api.time.upper_module.pipette.dispense(
            volume=50,
            height_offset=5,
        )
        is_last = i + 1 == len(wells)
        if is_last:
            sec += await robot_api.time.upper_module.pipette.blow_out()
        sec += await robot_api.time.upper_module.pipette.move_to(
            location=location(
                location_type=LocationType.CHIP_HOLDER,
                location_number=1,
                well=well,
                reference=LocationReference.TOP_JUST,
            ),
            z_speed=Speed.from_mm(10),
            optimize=True,
        )

    # upper_module
    await robot_api.upper_module.move_z_up()
    await robot_api.upper_module.move_to_ready()

    # upper_module.gripper
    await robot_api.upper_module.gripper.move_block_to_inspector(push=True)
    await robot_api.upper_module.gripper.move_block_to_holder()
    await robot_api.upper_module.gripper.open_lid(
        chip_holder_number=1,
        lid_holder_number=2,
    )
    await robot_api.upper_module.gripper.close_lid(
        lid_holder_number=2,
        chip_holder_number=1,
    )
    await robot_api.upper_module.gripper.move_labware(
        from_location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=1,
        ),
        to_location=location(
            location_type=LocationType.INSPECTOR,
        ),
    )
    await robot_api.upper_module.gripper.move_lid(
        from_location=location(
            location_type=LocationType.LID_HOLDER,
            location_number=1,
        ),
        to_location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=2,
        ),
    )
    await robot_api.upper_module.gripper.pick_labware(
        location=location(
            location_type=LocationType.INSPECTOR,
        ),
    )
    await robot_api.upper_module.gripper.place_labware(
        location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=1,
        ),
    )
    await robot_api.upper_module.gripper.pick_lid(
        location=location(
            location_type=LocationType.LID_HOLDER,
            location_number=1,
        ),
    )
    await robot_api.upper_module.gripper.place_lid(
        location=location(
            location_type=LocationType.CHIP_HOLDER,
            location_number=2,
        ),
    )
    await robot_api.upper_module.gripper.move_to(
        location=location(
            location_type=LocationType.DECK,
            location_number=1,
        ),
        z_gripper=ZGripper.UNDER_PLATE,
        slow_z_offset=5,
    )

    # upper_module.pipette
    await robot_api.upper_module.pipette.pick_up_tip(
        well="a1",
    )
    await robot_api.upper_module.pipette.drop_tip(
        location_type=LocationType.WASTE,
        # location_type=LocationType.TIP_RACK,
        well="a1",
    )
    await robot_api.upper_module.pipette.move_to(
        location=location(
            location_type=LocationType.RESERVOIR,
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(0, 0, 1.2),
        ),
    )
    await robot_api.upper_module.pipette.mix(
        volume=[50, 50],
        iteration=3,
        flow_rate=100,
    )
    await robot_api.upper_module.pipette.aspirate(
        volume=[50, 50],
        flow_rate=100,
    )
    wells = ["a1", "b1"]
    for i, well in enumerate(wells):
        await robot_api.upper_module.pipette.move_to(
            location=location(
                location_type=LocationType.CHIP_HOLDER,
                location_number=1,
                well=well,
                reference=LocationReference.BOTTOM,
            ),
        )
        await robot_api.upper_module.pipette.dispense(
            volume=50,
            height_offset=5,
        )
        is_last = i + 1 == len(wells)
        if is_last:
            await robot_api.upper_module.pipette.blow_out()
        await robot_api.upper_module.pipette.move_to(
            location=location(
                location_type=LocationType.CHIP_HOLDER,
                location_number=1,
                well=well,
                reference=LocationReference.TOP_JUST,
            ),
            z_speed=Speed.from_mm(10),
            optimize=True,
        )

    # deck_module.inspector
    await robot_api.deck_module.inspector.set_lcr_param(
        value=LCRParam(
            data_format_long=False,
            frequency=5000,
            voltage_level=2,
            measurement_time_mode=MeasurementTimeMode.MEDIUM,
            averaging_rate=1,
        )
    )
    lcr_values: dict[int, float] = await robot_api.deck_module.inspector.scan()
    await robot_api.deck_module.inspector.prepare_scan()
    # for i in range(192):
    for i in range(3):
        await robot_api.deck_module.inspector.set_switch_on(channel=i + 1)
        lcr_value: float = await robot_api.deck_module.inspector.get_lcr_value()
    await robot_api.deck_module.inspector.complete_scan()

    # deck_module.heater
    heater_on: dict[int, bool] = await robot_api.deck_module.heater.get_heater_on()
    heater_temperature: dict[int, float] = (
        await robot_api.deck_module.heater.get_temperature()
    )
    await robot_api.deck_module.heater.set_temperature(
        values={
            1: HeaterData(on=True, temperature=37.0),
            2: HeaterData(on=False),
            # ...
            8: HeaterData(on=True, temperature=37.5),
        }
    )

    # axis
    position = await robot_api.axis.get_position(axis=Axis.X)  # mm
    await robot_api.axis.set_speed(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.set_accel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.set_decel(axis=Axis.X, value=10)  # mm/sec2
    await robot_api.axis.disable(axis=Axis.X)
    await robot_api.axis.enable(axis=Axis.X)
    await robot_api.axis.stop(axis=Axis.X)
    await robot_api.axis.home(axis=Axis.X)
    await robot_api.axis.wait_home_done(axis=Axis.X)
    await robot_api.axis.jog(axis=Axis.X, value=10)  # mm/sec
    await robot_api.axis.step(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)
    await robot_api.axis.move(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)


if __name__ == "__main__":
    # asyncio.run(main())
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
