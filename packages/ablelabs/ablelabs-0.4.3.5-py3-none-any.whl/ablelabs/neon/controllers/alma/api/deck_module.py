import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.network.messenger import MessengerClient, run_server_func
from ablelabs.neon.utils.network.tcp_client import TcpClient
from ablelabs.neon.controllers.alma.api.robot_router import RobotRouter
from ablelabs.neon.controllers.alma.api.deck_modules.inspector import InspectorAPI
from ablelabs.neon.controllers.alma.api.deck_modules.heater import HeaterAPI


class DeckModuleAPI(MessengerClient):
    def __init__(self, tcp_client: TcpClient) -> None:
        super().__init__(tcp_client)
        self.inspector = InspectorAPI(tcp_client)
        self.heater = HeaterAPI(tcp_client)
