import cv2

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.kribb.api.robot_router import RobotRouter
from ablelabs.neon.common.notable.kribb.structs import LabelInfo, ColonyInfo


class OpticAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)

    @run_server_func(RobotRouter.optic_set_camera_live)
    async def set_camera_live(self, on: bool):
        pass

    @run_server_func(RobotRouter.optic_camera_capture)
    async def camera_capture(self, resize_ratio: float = None) -> cv2.Mat:
        pass

    @run_server_func(RobotRouter.optic_camera_show)
    async def camera_show(
        self,
        winname: str,
        resize_ratio: float = 0.5,
    ):
        pass

    @run_server_func(RobotRouter.optic_set_led_brightness)
    async def set_led_brightness(self, value: int):
        pass

    @run_server_func(RobotRouter.optic_set_led_on_off)
    async def set_led_on_off(self, on: bool):
        pass

    @run_server_func(RobotRouter.optic_set_displacement_zero)
    async def set_displacement_zero(self):
        pass

    @run_server_func(RobotRouter.optic_get_displacement_value)
    async def get_displacement_value(self) -> float:
        pass

    @run_server_func(RobotRouter.optic_detect_colony)
    async def detect_colony(
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
    ) -> tuple[tuple[int, int, int, int], list[LabelInfo], cv2.Mat, dict[str, cv2.Mat]]:
        pass

    @run_server_func(RobotRouter.optic_group_colony)
    async def group_colony(
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
    ) -> tuple[dict[int, list[LabelInfo]], cv2.Mat]:
        pass
