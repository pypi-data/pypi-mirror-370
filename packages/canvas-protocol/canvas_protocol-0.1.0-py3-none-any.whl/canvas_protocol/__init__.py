"""
A Python SDK for canvas.shymike.dev's WebSocket protocol.
"""

from .client.main import CanvasClient, Client

from .client.parser import (
    AllPixelsData,
    ErrorData,
    MessageParser,
    PixelColorData,
    SetPixelBroadcastData,
    parse_message,
)

from .color.color import Color

from .protocol.packing import (
    pack_coordinates,
    pack_rgb,
    unpack_coordinates,
    unpack_rgb,
)

from .protocol.requests import RequestType
from .protocol.responses import ResponseType
from .stats.stats import Stats

__all__ = [
    # Clients
    "Client",
    "CanvasClient",
    # Message parsing
    "MessageParser",
    "parse_message",
    "SetPixelBroadcastData",
    "PixelColorData",
    "ErrorData",
    "AllPixelsData",
    # Protocol types
    "RequestType",
    "ResponseType",
    # Packing utilities
    "pack_coordinates",
    "unpack_coordinates",
    "pack_rgb",
    "unpack_rgb",
    # Data types
    "Color",
    "Stats",
]
