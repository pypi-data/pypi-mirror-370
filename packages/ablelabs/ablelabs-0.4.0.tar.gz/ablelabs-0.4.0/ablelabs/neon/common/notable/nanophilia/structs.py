from dataclasses import dataclass

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.structs import Speed, FlowRate, LedBarParam
from ablelabs.neon.common.notable.nanophilia.enums import (
    LocationType,
    LocationReference,
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
