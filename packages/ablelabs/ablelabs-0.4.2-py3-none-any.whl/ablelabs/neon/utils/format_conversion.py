import struct
from typing import Literal


def floor_decimal(value: float, digit: int):
    """소수점 아래 자리수 자르기"""
    if digit == 0:
        return int(value)
    else:
        power_of_ten = 10**digit
        result: float = int(value * power_of_ten) / power_of_ten
        return result


def floor_precision(value: float, digit: int):
    """
    유효숫자 개수 자르기

    Examples:
        >>> floor_presicion(value=-123.45, digit=4)
        -123.4

        >>> floor_presicion(value=-123.45, digit=7)
        -123.45

        >>> floor_presicion(value=-123.45, digit=2)
        -120

        >>> floor_presicion(value=-123, digit=2)
        -120
    """
    value_str = str(value)
    number_str = value_str.replace(".", "").replace("-", "")
    if len(number_str) <= digit:
        return value
    else:
        if "." not in value_str:
            integer_part = value_str
        else:
            integer_part, fractional_part = value_str.split(".")

        integer_part_number_str = integer_part.replace("-", "")
        integer_part_count = len(integer_part_number_str)

        if integer_part_count > digit:  # 123.45, 2
            result_str = integer_part_number_str[:digit] + "0" * (
                integer_part_count - digit
            )
        elif integer_part_count == digit:  # 123.45, 3
            result_str = integer_part_number_str
        else:  # 123.45, 4
            result_str = (
                integer_part_number_str
                + "."
                + fractional_part[: digit - integer_part_count]
            )

        if value < 0:
            result_str = "-" + result_str
        return float(result_str)


def int_to_bytes(byteorder: Literal["little", "big"], value: int, length: int = None):
    if not length:
        length = (value.bit_length() + 7) // 8
    bytes_value = value.to_bytes(
        length=length,
        byteorder=byteorder,
        signed=value < 0,
    )
    return bytes_value


def int_to_2bytes(value: int):
    bytes_value = [(value >> 8) & 0xFF, value & 0xFF]
    return bytes_value


def bytes_to_int(byteorder: Literal["little", "big"], value: bytes):
    int_value = int.from_bytes(value, byteorder=byteorder, signed=True)
    return int_value


def bytes_to_bool(byteorder: Literal["little", "big"], value: bytes):
    int_value = bytes_to_int(byteorder=byteorder, value=value)
    bool_value = int_value == 1
    return bool_value


def int_to_bits(bit_count: int, value: int):
    bits_dict = {bit: value & (1 << bit) != 0 for bit in range(bit_count)}
    return bits_dict


def bytes_to_bits(byteorder: Literal["little", "big"], bit_count: int, value: bytes):
    int_value = bytes_to_int(byteorder=byteorder, value=value)
    bits_dict = int_to_bits(bit_count=bit_count, value=int_value)
    return bits_dict


def bytes_to_float(value: bytes):
    float_value = struct.unpack("f", value)[0]
    return float_value


def float_to_bytes(value: float):
    bytes_value = struct.pack("f", value)
    return bytes_value


def bytes_to_double(value: bytes):
    double_value: float = struct.unpack("!d", value)[0]
    return double_value


def str_to_bytes(value: str):
    bytes_value = value.encode()
    return bytes_value


def bytes_to_str(value: bytes):
    str_value: str = str(value, "ascii")
    return str_value


def str_to_ascii(value: str):
    bytes_value = [ord(ch) for ch in value]
    return bytes_value


def bytes_to_hex(byteorder: Literal["little", "big"], value: bytes):
    result = [int_to_hex(byteorder=byteorder, value=v) for v in value]
    return result


def int_to_hex(byteorder: Literal["little", "big"], value: int, pad_length: int = 1):
    min_length = (value.bit_length() + 7) // 8
    length = max(min_length, pad_length)
    result = [
        format(v, f"02x")
        for v in value.to_bytes(length, byteorder=byteorder, signed=value < 0)
    ]
    if len(result) == 1:
        result = result[0]
    return result


if __name__ == "__main__":
    assert (result := floor_precision(value=-123.45, digit=4)) == -123.4, result
    assert (result := floor_precision(value=-123.45, digit=7)) == -123.45, result
    assert (result := floor_precision(value=-123.45, digit=2)) == -120, result
    assert (result := floor_precision(value=-123, digit=2)) == -120, result
    assert (result := floor_precision(value=123, digit=2)) == 120, result
    assert (result := floor_precision(value=100.0, digit=3)) == 100, result
