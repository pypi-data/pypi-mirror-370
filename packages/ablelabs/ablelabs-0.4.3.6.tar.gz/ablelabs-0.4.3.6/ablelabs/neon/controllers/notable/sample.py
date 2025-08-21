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

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.controllers.notable.api.robot_api import RobotAPI
from ablelabs.neon.common.notable.enums import (
    Axis,
    LocationReference,
    RunStatus,
)
from ablelabs.neon.common.notable.structs import Speed, FlowRate, location


async def main():
    import subprocess

    # for windows.
    # subprocess.Popen(
    #     [
    #         r"C:\Users\ABLE Labs\Desktop\ABLE-Elba\robot\dist\Neon.exe",
    #     ]
    # )

    # for mac.
    subprocess.Popen(
        [
            r"/Users/sypark/Code/ABLE-Elba/.venv/bin/python",
            r"/Users/sypark/Code/ABLE-Elba/robot/src/controllers/notable/v2/robot_router.py",
        ],
        cwd=r"/Users/sypark/Code/ABLE-Elba",
    )
    await asyncio.sleep(1)

    ip = "localhost"
    port = 1234

    robot_api = RobotAPI()
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass

    await robot_api.wait_boot()
    await robot_api.set_run_status(RunStatus.READY)
    await robot_api.get_run_status()

    # set
    await robot_api.set.pipettes(
        {
            # 1: "8ch1000ul",
            2: "1ch200ul",
        }
    )
    await robot_api.set.tips(
        {
            # 1: "tip_1000",
            2: "tip_200",
        }
    )
    await robot_api.set.labwares(
        {
            1: "spl_trayplate_60ml_#30001",
            2: "spl_96_well_0.2ml_#30096",
            10: "ablelabs_tiprack_#AL-CT-200",
            11: "ablelabs_tiprack_#AL-CT-1000",
            12: "trash_#v2.5",
        }
    )

    # get
    await robot_api.get.pipette_infos()
    await robot_api.get.tip_infos()
    await robot_api.get.deck_module_infos()
    await robot_api.get.labware_infos()
    setup_data = await robot_api.get.setup_data()

    x, y, z = setup_data["teaching"]["pipette_1"]["8ch200ul"]["deck1_up"]
    setup_data["teaching"]["pipette_1"]["8ch200ul"]["deck1_up"] = [x + 1, y + 2, z + 3]
    await robot_api.set.update_setup_data(setup_data, True)

    # robot
    await robot_api.stop()
    await robot_api.clear_error()  # stop 이후, motion 전에.
    await robot_api.pause()
    await robot_api.resume()
    is_connected = await robot_api.is_connected()

    # motion
    await robot_api.motion.initialize()
    await robot_api.motion.move_to(
        pipette_number=2,
        location=location(
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
            offset=(1.0, 2.0, 3.0),
        ),
    )

    await robot_api.motion.pick_up_tip(
        pipette_number=2,
        location=location(
            location_number=10,
            well="a1",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=2,
        location=location(
            location_number=10,
            well="a1",
        ),
    )
    await robot_api.motion.pick_up_tip(
        pipette_number=2,
        location=location(
            location_number=10,
            well="a12",
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=2,
        location=location(
            location_number=12,
        ),
    )

    await robot_api.motion.aspirate(
        pipette_number=2,
        volume=200,
        location=location(
            location_number=1,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.rise_tip(
        pipette_number=2,
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.motion.dispense(
        pipette_number=2,
        volume=200,
        location=location(
            location_number=2,
            well="a1",
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.mix(
        pipette_number=2,
        volume=100,
        iteration=2,
        # location=location(
        #     location_number=2,
        #     well="a1",
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(70),
        delay=0.1,
    )
    await robot_api.motion.blow_out(
        pipette_number=2,
        flow_rate=FlowRate.from_ul(200),
    )
    await robot_api.motion.move_to_ready()

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
