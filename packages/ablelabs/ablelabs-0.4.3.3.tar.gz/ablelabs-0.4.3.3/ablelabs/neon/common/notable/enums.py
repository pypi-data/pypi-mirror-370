import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.utils.enum_types import StrEnum, auto, IntFlag, IntEnum, ItemGetable


class NUMBERING_ORDER(StrEnum):
    LTR_TTB = auto()  # Left to Right, Top to Bottom
    LTR_BTT = auto()  # Left to Right, Bottom to Top
    TTB_LTR = auto()  # Top to Bottom, Left to Right
    BTT_LTR = auto()  # Bottom to Top, Left to Right


class Color(IntFlag):
    NONE = 0
    RED = 1 << 0
    GREEN = 1 << 1
    BLUE = 1 << 2
    WHITE = 1 << 3
    CYAN = GREEN | BLUE
    MAGENTA = RED | BLUE
    YELLOW = RED | GREEN


class RunStatus(IntEnum):
    BOOT = auto()
    SHUTDOWN = auto()
    READY = auto()
    DONE = auto()
    INITIALIZE = auto()
    RUN = auto()
    PAUSE = auto()
    # 의도한 상황
    STOP = auto()
    EMERGENCY = auto()
    # 예기치 못한 상황
    ERROR = auto()  # 일반적인 에러
    TIMEOUT = auto()
    FAULT = auto()


class TaskStatus(StrEnum):
    RUNNING = auto()
    PAUSED = auto()
    STOPPED = auto()


class Axis(StrEnum):
    X = auto()
    Y = auto()
    Z1 = auto()
    Z2 = auto()
    P1 = auto()
    P2 = auto()

    @staticmethod
    def Z_(pipette_number: int):
        return Axis.from_str(f"{Axis.Z1[0]}{pipette_number}")

    @staticmethod
    def P_(pipette_number: int):
        return Axis.from_str(f"{Axis.P1[0]}{pipette_number}")

    Z = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.Z1[0]}{number}"))
    P = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.P1[0]}{number}"))


class LabwareType(StrEnum):
    TIP_RACK = auto()
    WASTE = auto()
    WELL_PLATE = auto()

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(str(__value).upper())


class Height(StrEnum):
    UP = auto()
    TOP = auto()
    TOP_JUST = auto()
    BOTTOM = auto()
    BOTTOM_JUST = auto()
    TIP_RACK_TOUCHED = auto()
    TIP_RACK_PRESSED = auto()
    WASTE_DROP_TIP = auto()
    WASTE_BLOW_OUT = auto()


class Plunger(StrEnum):
    HOME_OFFSET = auto()
    DROP_TIP = auto()
    TOP = auto()
    FIRST_STOP = auto()
    SECOND_STOP = auto()


class LocationType(StrEnum):
    DECK = auto()


class LocationReference(StrEnum):
    TOP = auto()
    TOP_JUST = auto()
    BOTTOM = auto()
    BOTTOM_JUST = auto()
