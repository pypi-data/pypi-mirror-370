import struct
from dataclasses import dataclass
from typing import List, Optional, Union

from ..color.color import Color
from ..protocol.packing import unpack_coordinates, unpack_rgb
from ..protocol.responses import ResponseType
from ..stats.stats import Stats


@dataclass
class SetPixelBroadcastData:
    """Represents a broadcasted pixel update from another client."""

    x: int
    y: int
    color: Color


@dataclass
class PixelColorData:
    """Represents the color of a requested pixel."""

    color: Color


@dataclass
class ErrorData:
    """Represents an error response from the server."""

    message: str


@dataclass
class AllPixelsData:
    """Represents all pixels from the canvas."""

    pixels: List[Color]


class MessageParser:
    """Parser for converting raw message data into structured objects based on response type."""

    @staticmethod
    def parse_message(
        response_type: ResponseType, data: bytes
    ) -> Optional[
        Union[SetPixelBroadcastData, PixelColorData, ErrorData, AllPixelsData, Stats]
    ]:
        """
        Parse raw message data based on the response type.
        """
        try:
            if response_type == ResponseType.SET_PIXEL_BROADCAST:
                return MessageParser._parse_set_pixel_broadcast(data)
            elif response_type == ResponseType.PIXEL_COLOR:
                return MessageParser._parse_pixel_color(data)
            elif response_type == ResponseType.ERROR:
                return MessageParser._parse_error(data)
            elif response_type == ResponseType.GET_ALL_PIXELS:
                return MessageParser._parse_all_pixels(data)
            elif response_type == ResponseType.STATS:
                return MessageParser._parse_stats(data)
            else:
                return None
        except (IndexError, struct.error, ValueError):
            return None

    @staticmethod
    def _parse_set_pixel_broadcast(data: bytes) -> Optional[SetPixelBroadcastData]:
        """Parse SetPixelBroadcast message: [x,y coordinates:3][rgb:3] = 6 bytes."""
        if len(data) < 6:
            return None

        x, y, _ = unpack_coordinates(data[0:3])
        rgb_value = unpack_rgb(data[3:6])

        color = Color(
            r=(rgb_value >> 16) & 0xFF,
            g=(rgb_value >> 8) & 0xFF,
            b=rgb_value & 0xFF,
        )

        return SetPixelBroadcastData(x=x, y=y, color=color)

    @staticmethod
    def _parse_pixel_color(data: bytes) -> Optional[PixelColorData]:
        """Parse PixelColor message: [rgb:3] = 3 bytes."""
        if len(data) < 3:
            return None

        rgb_value = unpack_rgb(data[0:3])
        color = Color(
            r=(rgb_value >> 16) & 0xFF,
            g=(rgb_value >> 8) & 0xFF,
            b=rgb_value & 0xFF,
        )

        return PixelColorData(color=color)

    @staticmethod
    def _parse_error(data: bytes) -> Optional[ErrorData]:
        """Parse Error message: [error_code:1] = 1 byte."""
        if len(data) < 1:
            return ErrorData(message="Unknown error")

        error_code = data[0]

        error_messages = {1: "Invalid message type", 2: "Coordinates out of bounds"}

        message = error_messages.get(error_code, f"Unknown error code: {error_code}")
        return ErrorData(message=message)

    @staticmethod
    def _parse_all_pixels(data: bytes) -> Optional[AllPixelsData]:
        """Parse GetAllPixels message: [rgb:3] repeated for each pixel."""
        pixels = []
        for i in range(0, len(data), 3):
            if i + 2 < len(data):
                rgb_value = unpack_rgb(data[i : i + 3])
                pixels.append(
                    Color(
                        r=(rgb_value >> 16) & 0xFF,
                        g=(rgb_value >> 8) & 0xFF,
                        b=rgb_value & 0xFF,
                    )
                )

        return AllPixelsData(pixels=pixels)

    @staticmethod
    def _parse_stats(data: bytes) -> Optional[Stats]:
        """Parse Stats message: [client_count:2][rps:4] = 6 bytes."""
        if len(data) < 6:
            return Stats(connected_clients=0, requests_per_second=0.0)

        client_count_bytes = data[0:2]
        rps_bytes = data[2:6]

        client_count = struct.unpack(">H", client_count_bytes)[
            0
        ]  # >H = big-endian uint16
        requests_per_second = struct.unpack(">f", rps_bytes)[
            0
        ]  # >f = big-endian float32

        return Stats(
            connected_clients=client_count,
            requests_per_second=requests_per_second,
        )


def parse_message(
    response_type: ResponseType, data: bytes
) -> Optional[
    Union[SetPixelBroadcastData, PixelColorData, ErrorData, AllPixelsData, Stats]
]:
    """
    Convenience function for parsing messages.

    """
    return MessageParser.parse_message(response_type, data)
