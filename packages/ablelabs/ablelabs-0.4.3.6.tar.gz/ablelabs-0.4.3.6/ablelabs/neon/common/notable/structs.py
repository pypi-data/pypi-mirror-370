from dataclasses import dataclass

import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.enums import Color, LocationType, LocationReference
from ablelabs.neon.utils.format_conversion import floor_precision


@dataclass
class Speed:
    unit: str
    unit_s: float = None
    rate: float = None

    def __str__(self) -> str:
        result = []
        if self.unit_s != None:
            result.append(f"{self.unit_s}{self.unit}/s")
        if self.rate != None:
            result.append(f"{floor_precision(self.rate * 100, digit=3)}%")
        return f"{' '.join(result)}"

    def __repr__(self) -> str:
        return self.__str__()

    # None인 속성 제외
    # def __repr__(self):
    #     field_strings = []
    #     for field in fields(self):
    #         value = getattr(self, field.name)
    #         if value is not None:
    #             field_strings.append(f"{field.name}={repr(value)}")
    #     field_string = ", ".join(field_strings)
    #     return f"{self.__class__.__name__}({field_string})"

    @staticmethod
    def from_mm(mm: float):
        return Speed(unit="mm", unit_s=mm)

    @staticmethod
    def from_rate(rate: float = 1.0):
        return Speed(unit="mm", rate=rate)


class FlowRate(Speed):
    @staticmethod
    def from_ul(ul: float):
        return Speed(unit="ul", unit_s=ul)

    @staticmethod
    def from_rate(rate: float = 1.0):
        return Speed(unit="ul", rate=rate)


@dataclass
class LedBarParam:
    color: Color = Color.NONE
    on_brightness_percent: int = None
    off_brightness_percent: int = None
    bar_percent: int = None
    blink_time_ms: int = None


@dataclass
class Location:
    location_type: LocationType
    location_number: int
    well: str
    reference: LocationReference
    offset: tuple[float] = (0, 0, 0)

    # def to(
    #     self,
    #     location_number: int = None,
    #     well: str = None,
    #     reference: LocationReference = None,
    #     offset: tuple[float] = None,
    # ):
    #     return Location(
    #         location_type=self.location_type,
    #         location_number=(
    #             location_number if location_number else self.location_number
    #         ),
    #         well=well if well else self.well,
    #         reference=reference if reference else self.reference,
    #         offset=offset if offset else self.offset,
    #     )

    def __str__(self) -> str:
        # inspect만으로는 원하는 형태로 만들기가 어려울 듯.
        # result = " ".join(
        #     [
        #         f"{name}={value}"
        #         for name, value in inspect.getmembers(self)
        #         if "__" not in name and not inspect.isfunction(value)
        #     ]
        # )
        # return result
        result = f"{self.location_type}"
        if self.location_number:
            result += f".{self.location_number}"
        if self.well:
            result += f" well={self.well}"
        if self.reference:
            result += f" reference={self.reference}"
        if self.offset and self.offset != (0, 0, 0):
            result += f" offset={self.offset}"
        return result

    def __repr__(self) -> str:
        return self.__str__()


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


if __name__ == "__main__":
    flow_rate = FlowRate.from_rate()
    print(flow_rate)
    flow_rate = FlowRate.from_rate(0.12345)
    print(flow_rate)
    flow_rate = FlowRate.from_rate(0.012345)
    print(flow_rate)

    led_bar_param = LedBarParam()
    print(led_bar_param)

    loc = Location(
        location_type=LocationType.DECK,
        location_number=12,
        well="a6",
        reference=LocationReference.BOTTOM,
        offset=(1, 2, 3),
    )
    print(loc)
