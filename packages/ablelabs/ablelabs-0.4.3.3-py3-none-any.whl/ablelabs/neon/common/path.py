import os
import sys
from loguru import logger

REQUIRED_FILES = [
    # "deck.json",
    "region.json",
    "pipette.json",
    "tip.json",
    "labware.json",
    "setup_data.toml",
    "driver_param.toml",
]


class Path:
    def __init__(
        self,
        required_files: list[str] = REQUIRED_FILES,
        required_dirs: list[str] = [],
    ) -> None:
        is_production = Path.is_production()
        root_path = Path.get_root_path()
        # print(f"root_path = {root_path}")
        if is_production:
            config_path = Path.get_config_path(root_path, required_files)
        else:
            config_path = Path.get_config_path(root_path, required_files, required_dirs)
        self._config_path = config_path
        logger.debug(f"root_path={root_path}  config_path={config_path}")
        # sypark platform 의존성 주입에 따라 경로 설정 변경 필요.
        # self.DECK_PATH = os.path.join(config_path, "deck.json")
        self.REGION_PATH = os.path.join(config_path, "region.json")
        self.PIPETTE_PATH = os.path.join(config_path, "pipette.json")
        self.TIP_PATH = os.path.join(config_path, "tip.json")
        self.DECK_MODULE_PATH = os.path.join(config_path, "deck_module.json")
        self.LABWARE_PATH = os.path.join(config_path, "labware.json")
        self.SETUP_DATA_PATH = os.path.join(config_path, "setup_data.toml")
        self.DRIVER_PARAM_PATH = os.path.join(config_path, "driver_param.toml")
        
    @property
    def config_path(self):
        return self._config_path

    @staticmethod
    def is_production() -> bool:
        """PyInstaller에 의해 배포되었는지 여부"""
        # return getattr(sys, "_MEIPASS", False)
        return getattr(
            sys, "frozen", False
        )  # cx_Freeze 같은 다른 패키징 도구에도 해당.

    @staticmethod
    def get_root_path() -> str:
        if Path.is_production():
            root_path = os.path.dirname(
                os.path.abspath(sys.executable)
            )  # 실행 파일 경로.
        else:
            root_path = os.path.abspath(os.curdir)  # 프로젝트 경로.
        return root_path

    @staticmethod
    def get_config_path(
        root_path: str, required_files: list[str], required_dirs: list[str] = []
    ):
        for dirpath, dirnames, filenames in os.walk(root_path):
            if all(required_dir in dirpath for required_dir in required_dirs) and all(
                required_file in filenames for required_file in required_files
            ):
                return dirpath
        return None
