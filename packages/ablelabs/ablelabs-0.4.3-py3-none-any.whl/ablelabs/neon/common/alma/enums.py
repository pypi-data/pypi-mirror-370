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
    LocationReference,
)
from ablelabs.neon.utils.enum_types import Enum, auto, StrEnum, ItemGetable


class DioInput(StrEnum):
    EMS = auto()
    DOOR_LEFT = auto()
    DOOR_RIGHT = auto()


class DioPDO(StrEnum):
    LED_LAMP = auto()


class Axis(StrEnum):
    X = auto()
    Y = auto()
    Z1 = auto()
    Z2 = auto()
    G = auto()
    P = auto()

    Z = ItemGetable[int](lambda number: Axis.from_str(f"{Axis.Z1[0]}{number}"))


class LocationType(StrEnum):
    READY = auto()
    LID_HOLDER = auto()
    BLOCK_HOLDER = auto()
    INSPECTOR = auto()
    DECK = auto()
    CHIP_HOLDER = auto()
    WASTE = auto()
    TIP_RACK = auto()
    RESERVOIR = auto()


class ZGripper(StrEnum):
    MOVE = auto()
    PLATE_LID_UNGRIP = auto()
    PLATE_LID_GRIP = auto()
    LID_UNGRIP = auto()
    LID_GRIP = auto()
    BLOCK_PUSH = auto()
    BLOCK_GRIP = auto()
    FORK = auto()
    UNDER_PLATE = auto()
    PUSH = auto()


class Gripper(StrEnum):
    UNGRIP = auto()
    PUSH = auto()
    GRIP_LID = auto()
    FORK = auto()
    GRIP_PLATE = auto()
    GRIP_BLOCK = auto()
    PUSH_BLOCK = auto()


class EquipmentStatus(StrEnum):
    NORMAL = auto()
    BLOCK_FORK = auto()
    BLOCK_GRIP = auto()
    CHIP_FORK = auto()
    CHIP_GRIP = auto()
    LID_GRIP = auto()
    INSPECTING = auto()
    PICKED_UP_TIP = auto()
    # ASPIRATING = auto()   # PICKED_UP_TIP으로 간주
