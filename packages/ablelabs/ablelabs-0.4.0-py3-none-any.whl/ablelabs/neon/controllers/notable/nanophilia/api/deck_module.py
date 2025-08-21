import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.notable.nanophilia.api.robot_router import RobotRouter
from ablelabs.neon.controllers.notable.nanophilia.api.deck_modules.washer_dryer import (
    WasherDryerAPI,
)
from ablelabs.neon.controllers.notable.nanophilia.api.deck_modules.magnetic_shaker import (
    MagneticShakerAPI,
)
from ablelabs.neon.controllers.notable.nanophilia.api.deck_modules.shaker import (
    ShakerAPI,
)


class DeckModuleAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)
        self.washer_dryer = WasherDryerAPI(tcp_client)
        self.magnetic_shaker = MagneticShakerAPI(tcp_client)
        self.shaker = ShakerAPI(tcp_client)
