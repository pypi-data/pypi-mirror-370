from typing import Tuple


def pack_coordinates(x: int, y: int, flag: bool = False) -> bytes:
    """Pack x, y coordinates and a boolean flag into a 3-byte representation."""
    packed = (int(flag) << 20) | (x << 10) | y
    return bytes([(packed >> 16) & 0xFF, (packed >> 8) & 0xFF, packed & 0xFF])


def unpack_coordinates(data: bytes) -> Tuple[int, int, bool]:
    """Unpack 3 bytes into x, y coordinates and a boolean flag.
    Layout: [flag:1][x:10][y:10] = 21 bits
    """
    packed = (data[0] << 16) | (data[1] << 8) | data[2]
    flag = (packed & (1 << 20)) != 0
    x = (packed >> 10) & 0x3FF
    y = packed & 0x3FF
    return (x, y, flag)


def pack_rgb(color: int) -> bytes:
    """Pack RGB color value into 3 bytes."""
    return bytes([(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF])


def unpack_rgb(data: bytes) -> int:
    """Unpack 3 bytes into RGB color value."""
    return (data[0] << 16) | (data[1] << 8) | data[2]
