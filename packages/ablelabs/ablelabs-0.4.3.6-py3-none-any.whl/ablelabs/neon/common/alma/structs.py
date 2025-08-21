from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.structs import Speed, FlowRate, LedBarParam
from ablelabs.neon.common.alma.enums import (
    LocationType,
    LocationReference,
    EquipmentStatus,
)


@dataclass
class Location:
    location_type: LocationType
    location_number: int = None
    well: str = None
    reference: LocationReference = None
    offset: tuple[float, float, float] = (0, 0, 0)

    def __str__(self):
        # 필드값이 기본값과 다를 때만 표시
        fields = []
        if self.location_number == None:
            fields.append(f"{self.location_type}")
        else:
            fields.append(f"{self.location_type}.{self.location_number}")
        if self.well != None:
            fields.append(f"well={self.well}")
        if self.reference != None:
            fields.append(f"reference={self.reference}")
        if self.offset != (0, 0, 0):
            fields.append(f"offset={self.offset}")
        return f"Location({', '.join(fields)})"


def location(
    location_type: LocationType = LocationType.DECK,
    location_number: int = None,
    well: str = None,
    reference: LocationReference = None,
    offset: tuple[float] = (0, 0, 0),
):
    return Location(
        location_type=location_type,
        location_number=location_number,
        well=well,
        reference=reference,
        offset=offset,
    )


class MeasurementTimeMode(Enum):
    SHORT = "SHOR"
    MEDIUM = "MED"
    LONG = "LONG"


@dataclass
class LCRParam:
    # preset value
    data_format_long: bool = False
    # function_impedance_type: MeasurementFunction = MeasurementFunction.CP_D
    frequency: float = 1000
    voltage_level: float = 1
    measurement_time_mode: MeasurementTimeMode = MeasurementTimeMode.MEDIUM
    averaging_rate: int = 1


class HeaterData(TypedDict):
    on: bool
    temperature: float


@dataclass
class State:
    equipment_status: EquipmentStatus = None
    location_type_number_well: tuple[LocationType, int, str] = None

    def to_dict(self):
        return {
            "equipment_status": self.equipment_status,
            "location_type_number_well": self.location_type_number_well,
        }

    @staticmethod
    def from_dict(data):
        data["equipment_status"] = EquipmentStatus(data["equipment_status"])
        data["location_type_number_well"] = (
            (
                LocationType(data["location_type_number_well"][0]),
                int(data["location_type_number_well"][1]),
                data["location_type_number_well"][2],
            )
            if data["location_type_number_well"]
            else None
        )
        return State(**data)

    def __str__(self):
        fields = []
        fields.append(f"{self.equipment_status}")
        if self.location_type_number_well != None:
            location_type, location_number, well = self.location_type_number_well
            location_str = location_type
            if location_number != None:
                location_str += f".{location_number}"
            if well != None:
                location_str += f"({well})"
            fields.append(f"{location_str}")
        return f"State({', '.join(fields)})"
