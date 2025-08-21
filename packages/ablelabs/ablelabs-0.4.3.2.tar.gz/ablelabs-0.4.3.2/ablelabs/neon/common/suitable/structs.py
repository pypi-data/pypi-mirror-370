from dataclasses import dataclass
import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.structs import Speed, FlowRate, LedBarParam
from ablelabs.neon.common.suitable.enums import LocationType, LocationReference


@dataclass
class Location:
    location_type: LocationType
    location_number: list[int]
    well: list[str]
    reference: LocationReference
    offset: tuple[float] = (0, 0, 0)

    def __post_init__(self):
        if self.location_number != None and self.well != None:
            assert len(self.location_number) == len(
                self.well
            ), f"not same len : location_number={self.location_number} well={self.well}"
        elif self.location_number == None and self.well != None:
            self.location_number = [None] * len(self.well)


def location(
    location_type: LocationType,
    location_number: list[int] = None,
    well: list[str] = None,
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


if __name__ == "__main__":
    loc = location(
        location_type=LocationType.DECK,
        location_number=[4, 4, 4],
        well=["a1", "b1", "c1"],
    )
    loc = location(
        location_type=LocationType.DECK,
        location_number=[22, 22, 16, 16, 10, 10, 4, 4],
        well=["a1", "c1", "a1", "c1", "a1", "c1", "a1", "c1"],
        reference=LocationReference.TOP,
    )
