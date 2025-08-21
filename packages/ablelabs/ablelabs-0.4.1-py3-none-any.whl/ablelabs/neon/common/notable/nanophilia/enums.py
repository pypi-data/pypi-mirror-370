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
    LocationType,
    LocationReference,
)
from ablelabs.neon.utils.enum_types import Enum, auto, StrEnum, ItemGetable


class WasherSuctionValve(StrEnum):
    NEEDLE = auto()
    BATH = auto()


class Axis(StrEnum):
    X = auto()
    Y = auto()
    Z1 = auto()
    Z2 = auto()
    P1 = auto()
    P2 = auto()

    WDX = auto()
    WDY = auto()
    WDZ = auto()
    WDP = auto()

    MSZ = auto()
    MSS = auto()

    Z = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.Z1[0]}{number}"))
    P = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.P1[0]}{number}"))


class DioInput(StrEnum):
    DOOR = auto()


class DioPDO(StrEnum):
    LED_LAMP = auto()


class AxisDO(StrEnum):
    WASHER_DRYER_FAN = auto()
    WASHER_DRYER_VALVE = auto()
    WASHER_DRYER_SUCTION_PUMP = auto()
