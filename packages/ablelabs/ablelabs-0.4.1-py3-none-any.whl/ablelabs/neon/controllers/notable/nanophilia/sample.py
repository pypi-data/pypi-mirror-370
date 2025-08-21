# python 3.10 버전

# 가상환경 설정
## python -m venv .venv
## py 3.10 -m venv .venv

# ablelabs 패키지 설치
## pip install ablelabs

# Neon.exe + resources 파일 위치 확인
## resources 폴더는 Neon.exe와 같은 폴더 또는 하위 폴더에

# subprocess.Popen으로 Neon.exe 실행

# connect -> wait_boot -> set_pipettes/tips/labwares 순서대로 호출


import asyncio
import sys, os
from typing import Literal

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.controllers.notable.nanophilia.api.robot_api import RobotAPI
from ablelabs.neon.common.notable.nanophilia.enums import (
    RunStatus,
    LocationType,
    Axis,
    LocationReference,
    DioInput,
    DioPDO,
    AxisDO,
)
from ablelabs.neon.common.notable.nanophilia.structs import Speed, FlowRate, location
from ablelabs.neon.utils.format_conversion import floor_decimal
from ablelabs.neon.utils.location_conversion import LocationConversion, NUMBERING_ORDER


async def main():
    import subprocess

    # for windows.
    # subprocess.Popen(
    #     [
    #         r"C:\your_path\Neon.exe",
    #     ]
    # )

    # for mac.
    subprocess.Popen(
        [
            r"/Users/sypark/Code/ABLE-Elba/.venv/bin/python",
            r"/Users/sypark/Code/ABLE-Elba/robot/src/controllers/notable/nanophilia/robot_router.py",
        ],
        cwd=r"/Users/sypark/Code/ABLE-Elba",
    )
    await asyncio.sleep(2)

    ip = "localhost"
    port = 1234

    robot_api = RobotAPI()
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass
    await robot_api.wait_boot()
    await robot_api.shutdown()

    # set
    await robot_api.set.pipettes(
        {
            1: "8ch200ul",
            2: "1ch200ul",
        }
    )
    await robot_api.set.tips(
        {
            1: "tip_200",
            2: "tip_200",
        }
    )
    await robot_api.set.deck_modules(
        {
            10: "magnetic_shaker",
            7: "shaker",
        }
    )
    await robot_api.set.labwares(
        {
            12: "trash_#v2.5",
            5: "megarobo_tipbox_#MCT200-N-TP-S-B",
            6: "megarobo_tipbox_#MCT200-N-TP-S-B",
            8: "megarobo_tipbox_#MCT200-N-TP-S-B",
            9: "megarobo_tipbox_#MCT200-N-TP-S-B",
            1: "spl_96_well_0.2ml_#30096",
            7: "spl_96_well_0.2ml_#30096",
            10: "spl_96_well_0.2ml_#30096",
            2: "NEST_12Channel_15ml_#360102",
        }
    )

    # get
    pipette_infos = await robot_api.get.pipette_infos()
    tip_infos = await robot_api.get.tip_infos()
    deck_module_infos = await robot_api.get.deck_module_infos()
    labware_infos = await robot_api.get.labware_infos()
    setup_data = await robot_api.get.setup_data()

    region_dataset = await robot_api.get.region_dataset()
    pipette_dataset = await robot_api.get.pipette_dataset()
    tip_dataset = await robot_api.get.tip_dataset()
    deck_module_dataset = await robot_api.get.deck_module_dataset()
    labware_dataset = await robot_api.get.labware_dataset()

    region_json = await robot_api.get.region_json()
    pipette_json = await robot_api.get.pipette_json()
    tip_json = await robot_api.get.tip_json()
    deck_module_json = await robot_api.get.deck_module_json()
    labware_json = await robot_api.get.labware_json()
    setup_data_toml = await robot_api.get.setup_data_toml()
    driver_param_toml = await robot_api.get.driver_param_toml()

    x, y, z = setup_data["teaching"]["pipette_1"]["8ch200ul"]["origin_1"]
    setup_data["teaching"]["pipette_1"]["8ch200ul"]["origin_1"] = [x + 1, y + 2, z + 3]
    await robot_api.set.update_setup_data(value=setup_data, save=True)
    await robot_api.set.update_pipette_attrs(
        value={
            1: {
                "blow_out_volume": 20,
            }
        }
    )

    # robot
    await robot_api.stop()
    await robot_api.clear_error()  # stop 이후, motion 전에.
    await robot_api.pause()
    await robot_api.resume()
    is_connected: dict[
        Literal[
            "motor",
            "dio",
            "shaker",
        ],
        bool,
    ] = await robot_api.is_connected()
    dio_input = await robot_api.get_dio_input()
    environment = await robot_api.get_environment()
    run_status = await robot_api.get_run_status()
    changed_robot_status = await robot_api.get_changed_robot_status()
    await robot_api.set_interlock(value=True)
    await robot_api.set_led_lamp(on=True)
    await robot_api.set_run_status(value=RunStatus.INITIALIZE)
    await robot_api.initialize()
    await robot_api.set_run_status(value=RunStatus.RUN)
    await robot_api.set_progress_rate(value=5)
    await robot_api.delay(sec=5)
    await robot_api.set_progress_rate(value=50)
    await robot_api.delay(sec=5)
    await robot_api.set_progress_rate(value=100)
    await robot_api.set_run_status(value=RunStatus.DONE)
    await robot_api.set_run_status(value=RunStatus.READY)

    # FFU
    ffu_status = await robot_api.get_ffu()  # 상태 조회
    await robot_api.set_ffu(on=True, rpm=1000)  # FFU 켜기, RPM 설정
    await robot_api.set_ffu(on=False)  # FFU 끄기
    await robot_api.set_ffu_alarm_clear()  # 알람 클리어

    # cold plate
    coldplate_temperature = await robot_api.get_coldplate_temperature()
    await robot_api.set_coldplate_temperature(on=True, value=-10)
    await robot_api.set_coldplate_temperature(on=False)

    # motion
    await robot_api.motion.initialize()
    await robot_api.motion.move_to(
        pipette_number=1,
        location=location(
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(1.0, 2.0, 3.0),
        ),
    )

    await robot_api.motion.pick_up_tip(
        pipette_number=1,
        location=location(
            location_number=5,
            well="a1",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=1,
        location=location(
            location_number=5,
            well="a1",
        ),
    )
    await robot_api.motion.pick_up_tip(
        pipette_number=1,
        location=location(
            location_number=5,
            well="a12",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=1,
        location=location(
            location_number=12,
        ),
    )

    await robot_api.motion.aspirate(
        pipette_number=1,
        volume=20,
        location=location(
            location_number=2,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.rise_tip(
        pipette_number=1,
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.motion.dispense(
        pipette_number=1,
        volume=20,
        location=location(
            location_number=1,
            well="a2",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.mix(
        pipette_number=1,
        volume=20,
        iteration=2,
        # location=location(
        #     location_number=1,
        #     well="a3",
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(20),
        delay=0.1,
    )
    await robot_api.motion.blow_out(
        pipette_number=1,
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.ready_plunger(
        pipette_number=1,
        flow_rate=FlowRate.from_ul(20),
    )
    await robot_api.motion.move_z_up()
    await robot_api.motion.move_to_ready()

    # deck_module.washer_dryer
    await robot_api.deck_module.washer_dryer.off_do()
    await robot_api.deck_module.washer_dryer.initialize()
    await robot_api.deck_module.washer_dryer.move_to_ready()
    await robot_api.deck_module.washer_dryer.move_to_washing()
    await robot_api.deck_module.washer_dryer.move_to(
        column=1,
        offset=(0.1, 0.2, 0.3),
    )
    await robot_api.deck_module.washer_dryer.prime(sec=5)
    await robot_api.deck_module.washer_dryer.recovery(sec=5)
    await robot_api.deck_module.washer_dryer.suction(
        columns=[1, 4, 7, 10],
        depth=10,
        z_speed=Speed.from_mm(5),
        delay_sec=0.1,
    )
    await robot_api.deck_module.washer_dryer.dispense(
        columns=[1, 4, 7, 10],
        volume=100,
    )
    await robot_api.deck_module.washer_dryer.wash_needle(
        depth=5,
        delay_sec=0.5,
    )
    await robot_api.deck_module.washer_dryer.wash_tube(
        cycle=3,
        suction_sec=1.0,
        dispense_sec=1.0,
    )
    await robot_api.deck_module.washer_dryer.dry(sec=3)

    # deck_module.magnetic_shaker
    await robot_api.deck_module.magnetic_shaker.initialize()
    await robot_api.deck_module.magnetic_shaker.magnet(on=True)
    await robot_api.deck_module.magnetic_shaker.magnet(on=False)
    await robot_api.deck_module.magnetic_shaker.shake(
        rpm=500,
        acceleration_sec=5,
    )
    await asyncio.sleep(5)
    await robot_api.deck_module.magnetic_shaker.shake_off()
    await robot_api.deck_module.magnetic_shaker.move_to_ready()

    # deck_module.shaker
    await robot_api.deck_module.shaker.initialize()
    await robot_api.deck_module.shaker.shake(
        rpm=500,
        acceleration_sec=5,
    )
    await asyncio.sleep(5)
    await robot_api.deck_module.shaker.shake_off()
    await robot_api.deck_module.shaker.move_to_ready()

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
    await robot_api.axis.jog(axis=Axis.X, value=0)  # mm/sec
    await robot_api.axis.step(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)
    await robot_api.axis.move(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.create_task(main())
    loop.run_forever()
