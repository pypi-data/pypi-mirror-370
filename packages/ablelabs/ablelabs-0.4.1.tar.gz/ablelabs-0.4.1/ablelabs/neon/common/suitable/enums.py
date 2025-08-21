import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.enums import (
    NUMBERING_ORDER,
    Color,
    RunStatus,
    TaskStatus,
    LabwareType,
    Height,
    Plunger,
)
from ablelabs.neon.utils.enum_types import Enum, auto, StrEnum, ItemGetable


class LedLamp(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()


class Buzzer(Enum):
    DONE = auto()
    ERROR = auto()


class Axis(StrEnum):
    X = auto()
    Y1 = auto()
    Y2 = auto()
    Y3 = auto()
    Y4 = auto()
    Y5 = auto()
    Y6 = auto()
    Y7 = auto()
    Y8 = auto()
    Z1 = auto()
    Z2 = auto()
    Z3 = auto()
    Z4 = auto()
    Z5 = auto()
    Z6 = auto()
    Z7 = auto()
    Z8 = auto()
    P1 = auto()
    P2 = auto()
    P3 = auto()
    P4 = auto()
    P5 = auto()
    P6 = auto()
    P7 = auto()
    P8 = auto()

    Y = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.Y1[0]}{number}"))
    Z = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.Z1[0]}{number}"))
    P = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.P1[0]}{number}"))


class LocationType(StrEnum):
    READY = auto()
    DECK = auto()
    TUBE_384 = auto()
    TEST_TUBE = auto()
    BALANCE = auto()
    WASTE = auto()


class LocationReference(StrEnum):
    TOP = auto()
    TOP_JUST = auto()
    BOTTOM = auto()
    BOTTOM_JUST = auto()
    LIQUID = auto()  # for LLD only when aspirate


class AssignmentStatus(StrEnum):
    NOT_ASSIGNED = auto()
    ASSIGNING = auto()
    ASSIGNED = auto()


class MotionStr(StrEnum):
    READY = auto()
    INITIALIZE = auto()
    PICK_UP_TIP = auto()
    ASPIRATE = auto()
    DISPENSE = auto()
    DROP_TIP = auto()


class PipetteCalibrationType(StrEnum):
    Tip_1000_DW = auto()
    Tip_1000_ACN = auto()
    Tip_200_ACN = auto()


if __name__ == "__main__":
    y1 = Axis.Y[1]
    print(y1)
