import asyncio
from loguru import logger

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.suitable.sara.api.robot_router import RobotRouter
from ablelabs.neon.controllers.suitable.sara.api.get_api import GetAPI
from ablelabs.neon.controllers.suitable.sara.api.set_api import SetAPI
from ablelabs.neon.controllers.suitable.sara.api.time_api import TimeAPI
from ablelabs.neon.controllers.suitable.sara.api.motion_api import MotionAPI
from ablelabs.neon.controllers.suitable.sara.api.axis_api import AxisAPI
from ablelabs.neon.common.suitable.constants import PIPETTE_NUMBERS
from ablelabs.neon.common.suitable.enums import (
    LocationType,
    Axis,
    LocationReference,
    RunStatus,
    PipetteCalibrationType,
)
from ablelabs.neon.common.suitable.structs import Speed, FlowRate, location


class RobotAPI(MessengerClient):
    def __init__(self) -> None:
        tcp_client = TcpClient(name="tcp_client", log_func=logger.trace)
        super().__init__(tcp_client)
        self._get_api = GetAPI(tcp_client=tcp_client)
        self._set_api = SetAPI(tcp_client=tcp_client)
        self._time_api = TimeAPI(tcp_client=tcp_client)
        self._motion_api = MotionAPI(tcp_client=tcp_client)
        self._axis_api = AxisAPI(tcp_client=tcp_client)

    @property
    def get(self):
        return self._get_api

    @property
    def set(self):
        return self._set_api

    @property
    def time(self):
        return self._time_api

    @property
    def motion(self):
        return self._motion_api

    @property
    def axis(self):
        return self._axis_api

    async def connect(self, ip, port):
        await self._tcp_client.connect(ip=ip, port=port)

    @run_server_func(RobotRouter.robot_wait_boot)
    async def wait_boot(self):
        pass

    @run_server_func(RobotRouter.robot_stop)
    async def stop(self):
        pass

    @run_server_func(RobotRouter.robot_clear_error)
    async def clear_error(self):
        pass

    @run_server_func(RobotRouter.robot_pause)
    async def pause(self):
        pass

    @run_server_func(RobotRouter.robot_resume)
    async def resume(self):
        pass

    @run_server_func(RobotRouter.robot_is_connected)
    async def is_connected(self):
        pass

    @run_server_func(RobotRouter.robot_get_run_status)
    async def get_run_status(self) -> dict[str, RunStatus | bool]:
        pass

    @run_server_func(RobotRouter.robot_get_changed_robot_status)
    async def get_changed_robot_status(self) -> dict[str, RunStatus | bool]:
        pass

    @run_server_func(RobotRouter.robot_set_run_status)
    async def set_run_status(self, value: RunStatus):
        pass

    @run_server_func(RobotRouter.robot_set_progress_rate)
    async def set_progress_rate(self, value: float):
        pass

    @run_server_func(RobotRouter.robot_set_interlock)
    async def set_interlock(self, value: bool):
        pass


async def main():
    import subprocess

    # for windows.
    # root = r"D:\Code\ABLE-Elba"
    # subprocess.Popen(
    #     [
    #         rf"{root}\.venv\Scripts\python.exe",
    #         rf"{root}\robot\src\controllers\suitable\sara\robot_router.py",
    #     ],
    #     cwd=root,
    # )
    # await asyncio.sleep(1)

    # for mac.
    # subprocess.Popen(
    #     [
    #         r"/Users/sypark/Code/ABLE-Elba/.venv/bin/python",
    #         r"/Users/sypark/Code/ABLE-Elba/robot/src/controllers/suitable/sara/robot_router.py",
    #     ],
    #     cwd=r"/Users/sypark/Code/ABLE-Elba",
    # )
    # await asyncio.sleep(1)

    logger.remove()
    # logger.add(sys.stdout, level="TRACE")
    # logger.add(sys.stdout, level="DEBUG")
    logger.add(sys.stdout, level="INFO")
    # logger.add("logs/trace.log", level="TRACE")
    # logger.add("logs/debug.log", level="DEBUG")
    logger.add("logs/info.log", level="INFO")

    ip = "localhost"
    port = 1234

    robot_api = RobotAPI()
    try:
        await robot_api.connect(ip=ip, port=port)
    except Exception as e:
        pass

    # get
    logger.info(f"setup_data = {await robot_api.get.setup_data()}")

    # set
    await robot_api.set.pipettes({n: "1ch1000ul" for n in PIPETTE_NUMBERS})
    await robot_api.set.tips({n: "tip_1000" for n in PIPETTE_NUMBERS})
    await robot_api.set.labwares(
        {
            21: "ablelabs_tiprack_200ul",
            22: "ablelabs_tiprack_200ul",
            23: "ablelabs_tiprack_200ul",
            24: "ablelabs_tiprack_200ul",
            4: "ablelabs_tiprack_1000ul",
            6: "ablelabs_tiprack_1000ul",
            # 5: "spl_dw_reservoir",
            5: "ablelabs_acn_reservoir",
            15: "bioneer_96_qc_plate",
            16: "bioneer_96_qc_plate",
            9: "bioneer_96_qc_plate",
            # 10: "bioneer_96_qc_plate",
            10: "bioneer_384_qc_plate",
            13: "spl_96_deep_well_plate",
            14: "spl_96_deep_well_plate",
            7: "spl_96_deep_well_plate",
            8: "spl_96_deep_well_plate",
            17: "spl_96_deep_well_plate",
            18: "spl_96_deep_well_plate",
            11: "spl_96_deep_well_plate",
            12: "spl_96_deep_well_plate",
        }
    )
    await robot_api.set.update_pipette_attrs(
        {n: {"blow_out_volume": 20} for n in PIPETTE_NUMBERS}
    )
    await robot_api.set.pipette_calibrations(
        {n: PipetteCalibrationType.Tip_1000_DW for n in PIPETTE_NUMBERS}
    )

    # robot
    await robot_api.stop()
    await robot_api.clear_error()  # stop 이후, motion 전에. / fault 후에.
    await robot_api.pause()
    await robot_api.resume()
    logger.info(f"is_connected = {await robot_api.is_connected()}")
    await robot_api.set_run_status(RunStatus.INITIALIZE)
    await robot_api.set_run_status(RunStatus.RUN)
    await robot_api.set_progress_rate(5)
    await robot_api.set_interlock(False)
    logger.info(f"get_run_status = {await robot_api.get_run_status()}")

    async def get_changed_robot_status():
        while True:
            robot_status = await robot_api.get_changed_robot_status()
            logger.info(f"robot_status = {robot_status}")

    asyncio.create_task(get_changed_robot_status())
    await asyncio.sleep(0.5)
    await robot_api.set_run_status(RunStatus.DONE)

    # time
    await robot_api.time.initialize()
    await robot_api.time.move_to_ready()
    await robot_api.time.move_to(
        pipette_number=[1, 2, 3],
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4],
            well=["a1", "b1", "c1"],
        ),
    )

    await robot_api.time.pick_up_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.time.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.time.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.WASTE,
        ),
    )

    await robot_api.time.aspirate(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[2, 2, 2, 2, 2, 2, 2, 2],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.LIQUID,
        ),
        flow_rate=FlowRate.from_ul(100),
        rise_tip_height_offset=5,
        pre_wet_count=3,
    )
    await robot_api.time.rise_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.time.dispense(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4, 4, 4, 4, 4, 4],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.time.mix(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=100,
        iteration=2,
        # location=location(
        #     location_type=LocationType.DECK,
        #     location_number=[4, 4, 4, 4, 4, 4, 4, 4],
        #     well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(70),
        delay=0.1,
    )
    await robot_api.time.blow_out(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        flow_rate=FlowRate.from_ul(200),
    )

    # motion
    await robot_api.motion.initialize()
    await robot_api.motion.home_z()
    await robot_api.motion.home_x()
    await robot_api.motion.home_y()
    await robot_api.motion.home_p()

    await robot_api.set.tips({n: "tip_1000" for n in PIPETTE_NUMBERS})
    await robot_api.motion.move_to(
        pipette_number=[1, 2, 3],
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4],
            well=["a1", "b1", "c1"],
        ),
    )

    await robot_api.motion.pick_up_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.DECK,
            location_number=[3, 3, 3, 3, 3, 3, 3, 3],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        ),
    )
    await robot_api.motion.drop_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        location=location(
            location_type=LocationType.WASTE,
        ),
    )

    await robot_api.motion.aspirate(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[2, 2, 2, 2, 2, 2, 2, 2],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.LIQUID,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.rise_tip(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        height_offset=5,
        z_speed=Speed.from_mm(2),
    )
    await robot_api.motion.dispense(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=200,
        location=location(
            location_type=LocationType.DECK,
            location_number=[4, 4, 4, 4, 4, 4, 4, 4],
            well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=FlowRate.from_ul(100),
    )
    await robot_api.motion.mix(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        volume=100,
        iteration=2,
        # location=location(
        #     location_type=LocationType.DECK,
        #     location_number=[4, 4, 4, 4, 4, 4, 4, 4],
        #     well=["a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"],
        #     reference=LocationReference.BOTTOM,
        # ),
        flow_rate=FlowRate.from_ul(70),
        delay=0.1,
    )
    await robot_api.motion.blow_out(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
        flow_rate=FlowRate.from_ul(200),
    )

    await robot_api.motion.aspirate(
        pipette_number=[1, 2, 3],
        volume=[[200, 100, 50]],
        location=location(
            location_type=LocationType.DECK,
            location_number=[2, 2, 2],
            well=["a1", "b1", "c1"],
            reference=LocationReference.BOTTOM,
        ),
        flow_rate=[FlowRate.from_ul(100), FlowRate.from_ul(80), FlowRate.from_ul(60)],
    )
    await robot_api.motion.blow_out(
        pipette_number=[1, 2, 3, 4, 5, 6, 7, 8],
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
    await robot_api.axis.step(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)
    await robot_api.axis.move(axis=Axis.X, value=10)  # mm
    await robot_api.axis.wait_move_done(axis=Axis.X)


if __name__ == "__main__":
    asyncio.run(main())
