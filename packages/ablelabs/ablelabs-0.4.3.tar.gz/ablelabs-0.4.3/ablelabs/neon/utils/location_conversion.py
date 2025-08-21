import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.notable.enums import NUMBERING_ORDER


class LocationConversion:
    @staticmethod
    def get_row_column(
        row_count: int,
        col_count: int,
        numbering_order: NUMBERING_ORDER,
        number: int,
        base: int = 1,
    ):
        if numbering_order == NUMBERING_ORDER.LTR_TTB:
            row, column = divmod(number - base, col_count)
        elif numbering_order == NUMBERING_ORDER.LTR_BTT:
            row, column = divmod(number - base, col_count)
        elif numbering_order == NUMBERING_ORDER.TTB_LTR:
            # row, column = divmod(number - base, row_count)
            # row = row_count - 1 - row
            raise NotImplementedError()
        row += base
        column += base
        return row, column

    @staticmethod
    def get_well(row: int, column: int, base: int = 1):
        well_row = chr(ord("A") + row - base)
        well_col = column + 1 - base
        return f"{well_row}{well_col}"

    @staticmethod
    def _get_cell(
        row_count: int,
        col_count: int,
        numbering_order: NUMBERING_ORDER,
        row: int,
        col: int,
        base: int = 1,
    ):
        if numbering_order == NUMBERING_ORDER.LTR_TTB:
            cell = (row - base) * col_count + col
        elif numbering_order == NUMBERING_ORDER.LTR_BTT:
            cell = (row_count - 1 - row + base) * col_count + col
        elif numbering_order == NUMBERING_ORDER.TTB_LTR:
            # cell = (row - base) * col_count + col
            raise NotImplementedError()
        return cell

    @staticmethod
    def well_row_column(
        labware_row: int,
        labware_col: int,
        numbering_order: NUMBERING_ORDER,
        well_str: str,
        base: int = 1,
    ):
        well_index: int = LocationConversion.well_str_to_well_index(
            labware_row=labware_row,
            labware_col=labware_col,
            numbering_order=numbering_order,
            well_str=well_str,
            base=base,
        )
        return LocationConversion.get_row_column(
            row_count=labware_row,
            col_count=labware_col,
            numbering_order=numbering_order,
            number=well_index,
            base=base,
        )

    @staticmethod
    def well_str_to_well_index(
        labware_row: int,
        labware_col: int,
        numbering_order: NUMBERING_ORDER,
        well_str: str,
        base: int = 1,
    ):
        well_row = ord(well_str[0].upper()) - ord("A") + base
        well_col = int(well_str[1:]) - 1 + base
        return LocationConversion._get_cell(
            row_count=labware_row,
            col_count=labware_col,
            numbering_order=numbering_order,
            row=well_row,
            col=well_col,
            base=base,
        )

    @staticmethod
    def well_index_to_well_str(
        labware_row: int,
        labware_col: int,
        numbering_order: NUMBERING_ORDER,
        well_index: int,
        base: int = 1,
    ):
        row, column = LocationConversion.get_row_column(
            row_count=labware_row,
            col_count=labware_col,
            numbering_order=numbering_order,
            number=well_index,
            base=base,
        )
        return LocationConversion.get_well(row=row, column=column, base=base)

    # @staticmethod
    # def str_bool_list_to_index_list(
    #     row_count: int,
    #     col_count: int,
    #     value: list[str],
    #     numbering_order: NUMBERING_ORDER,
    #     base: int = 1,
    #     sort: bool = True,
    # ):
    #     row_columns: list[tuple[int, int]] = []
    #     for row, rows in enumerate(value):
    #         for column, cell in enumerate(rows):
    #             if cell == "1":
    #                 row_columns.append((row + base, column + base))
    #     result = [
    #         LocationConversion.get_cell(
    #             row_count=row_count,
    #             col_count=col_count,
    #             numbering_order=numbering_order,
    #             row=row,
    #             col=column,
    #             base=base,
    #         )
    #         for row, column in row_columns
    #     ]
    #     if sort:
    #         result.sort()
    #     return result


if __name__ == "__main__":

    class RegionSample:
        def __init__(
            self, row: int, col: int, numbering_order: NUMBERING_ORDER
        ) -> None:
            self.row = row
            self.col = col
            self.numbering_order = numbering_order

    deck = RegionSample(row=4, col=3, numbering_order=NUMBERING_ORDER.LTR_BTT)
    well_plate_96 = RegionSample(row=8, col=12, numbering_order=NUMBERING_ORDER.LTR_TTB)

    row_column = LocationConversion.get_row_column(
        row_count=deck.row,
        col_count=deck.col,
        numbering_order=deck.numbering_order,
        number=1,
    )
    print(f"deck(1) = {row_column}")

    row_column = LocationConversion.get_row_column(
        row_count=deck.row,
        col_count=deck.col,
        numbering_order=deck.numbering_order,
        number=4,
    )
    print(f"deck(4) = {row_column}")

    row_column = LocationConversion.get_row_column(
        row_count=deck.row,
        col_count=deck.col,
        numbering_order=deck.numbering_order,
        number=12,
    )
    print(f"deck(12) = {row_column}")

    row_column = LocationConversion.well_row_column(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_str="a1",
    )
    print(f"well_plate_96(a1) = {row_column}")

    row_column = LocationConversion.well_row_column(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_str="a12",
    )
    print(f"well_plate_96(a12) = {row_column}")

    row_column = LocationConversion.well_row_column(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_str="h12",
    )
    print(f"well_plate_96(h12) = {row_column}")

    row_column = LocationConversion.well_row_column(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_str="b3",
    )
    print(f"well_plate_96(b3) = {row_column}")

    well = LocationConversion.get_well(row=1, column=1)
    print(f"well(1,1) = {well}")

    well = LocationConversion.get_well(row=1, column=12)
    print(f"well(1,12) = {well}")

    well = LocationConversion.get_well(row=8, column=12)
    print(f"well(8,12) = {well}")

    well = LocationConversion.get_well(row=16, column=24)
    print(f"well(16,24) = {well}")

    well = LocationConversion.well_index_to_well_str(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_index=1,
    )
    print(f"well_plate_96(1) = {well}")

    well = LocationConversion.well_index_to_well_str(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_index=12,
    )
    print(f"well_plate_96(12) = {well}")

    well = LocationConversion.well_index_to_well_str(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_index=96,
    )
    print(f"well_plate_96(96) = {well}")

    well = LocationConversion.well_index_to_well_str(
        labware_row=well_plate_96.row,
        labware_col=well_plate_96.col,
        numbering_order=well_plate_96.numbering_order,
        well_index=15,
    )
    print(f"well_plate_96(15) = {well}")
