# Import from new structure
from ablelabs.neon_v2.notable.resource.driver_param import DriverParam
from ablelabs.neon_v2.notable.resource.setup_data import SetupData
from ablelabs.neon_v2.notable.resource.library import Library
from ablelabs.neon_v2.notable.config.pipette import Pipette
from ablelabs.neon_v2.notable.config.deck import Deck
from ablelabs.neon_v2.notable.driver.io import IO
from ablelabs.neon_v2.notable.driver.axis import Axis
from ablelabs.neon_v2.notable.controller.upper_module import UpperModule
from ablelabs.neon_v2.notable.action.robot import Robot


class Notable:
    def __init__(self, base_url: str):
        self._base_url = base_url

        self.resource = Resource(base_url)
        self.config = Config(base_url)
        self.driver = Driver(base_url)
        self.controller = Controller(base_url)
        self.action = Action(base_url)


class Resource:
    def __init__(self, base_url: str):
        self.driver_param = DriverParam(base_url)
        self.setup_data = SetupData(base_url)
        self.library = Library(base_url)


class Config:
    def __init__(self, base_url: str):
        self.pipette = Pipette(base_url)
        self.deck = Deck(base_url)


class Driver:
    def __init__(self, base_url: str):
        self.io = IO(base_url)
        self.axis = Axis(base_url)


class Controller:
    def __init__(self, base_url: str):
        self.upper_module = UpperModule(base_url)


class Action:
    def __init__(self, base_url: str):
        self.robot = Robot(base_url)
