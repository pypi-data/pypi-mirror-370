import asyncio
import struct
from typing import List, Optional, Union
from websockets.protocol import State

import websockets
from websockets.exceptions import WebSocketException

from ..color.color import Color
from ..protocol.packing import (
    pack_coordinates,
    pack_rgb,
    unpack_rgb,
)
from ..protocol.requests import RequestType
from ..protocol.responses import ResponseType
from ..stats.stats import Stats


class Client:
    """A WebSocket client that supports both manual connection management and context manager usage."""

    def __init__(self, uri: str):
        self.uri = uri
        self._websocket: Optional[websockets.WebSocketClientProtocol] = None

    @property
    def is_connected(self) -> bool:
        """Check if the client is currently connected."""
        if self._websocket is None:
            return False

        return self._websocket.state == State.OPEN

    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        if self.is_connected:
            return

        try:
            self._websocket = await websockets.connect(self.uri, max_size=4 * 1024 * 1024) # 4 MB
        except WebSocketException as e:
            raise ConnectionError(f"Failed to connect to {self.uri}: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        if self._websocket:
            if self._websocket.state == State.OPEN:
                await self._websocket.close()

        self._websocket = None

    async def send(self, message: bytes) -> None:
        """Send a message to the server."""
        if not self.is_connected or self._websocket is None:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            await self._websocket.send(message)
        except WebSocketException as e:
            raise ConnectionError(f"Failed to send message: {e}") from e

    async def receive(self) -> websockets.Data:
        """Receive a message from the server."""
        if not self.is_connected or self._websocket is None:
            raise RuntimeError("Client is not connected. Call connect() first.")

        try:
            return await self._websocket.recv()
        except WebSocketException as e:
            raise ConnectionError(f"Failed to receive message: {e}") from e

    async def __aenter__(self) -> "Client":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()


class CanvasClient(Client):
    """A specialized WebSocket client for the Canvas protocol."""

    def __init__(self, uri: str):
        super().__init__(uri)

    async def set_pixel(
        self, x: int, y: int, color: Union[Color, int], confirmation: bool = True
    ) -> None:
        """Send a pixel update to the server."""
        message = bytes(
            [
                RequestType.SET_PIXEL.value,
                *pack_coordinates(x, y, not confirmation),
                *pack_rgb(color.to_int() if isinstance(color, Color) else color),
            ]
        )
        await self.send(message)

    async def get_pixel(self, x: int, y: int) -> None:
        """Request the color of a specific pixel from the server."""
        message = bytes([RequestType.GET_PIXEL.value, *pack_coordinates(x, y)])
        await self.send(message)

    async def get_all_pixels(self) -> None:
        """Request all pixel colors from the server."""
        message = bytes([RequestType.GET_ALL_PIXELS.value])
        await self.send(message)

    async def get_stats(self) -> None:
        """Request statistics from the server."""
        message = bytes([RequestType.GET_STATS.value])
        await self.send(message)

    async def receive_pixel_color(self) -> Color:
        """Wait for and parse a pixel color response."""
        while True:
            data = await self.receive()
            if isinstance(data, bytes) and len(data) > 0:
                try:
                    response_type = ResponseType(data[0])
                    if response_type == ResponseType.PIXEL_COLOR:
                        # parse pixel color from response
                        if len(data) >= 4:
                            rgb_value = unpack_rgb(data[1:4])
                            return Color(
                                r=(rgb_value >> 16) & 0xFF,
                                g=(rgb_value >> 8) & 0xFF,
                                b=rgb_value & 0xFF,
                            )
                except ValueError:
                    continue

    async def receive_all_pixels(self) -> List[Color]:
        """Wait for and parse all pixels response."""
        while True:
            data = await self.receive()
            if isinstance(data, bytes) and len(data) > 0:
                try:
                    response_type = ResponseType(data[0])
                    if response_type == ResponseType.GET_ALL_PIXELS:
                        # parse all pixels from response
                        pixels = []
                        for i in range(1, len(data), 3):
                            if i + 2 < len(data):
                                rgb_value = unpack_rgb(data[i : i + 3])
                                pixels.append(
                                    Color(
                                        r=(rgb_value >> 16) & 0xFF,
                                        g=(rgb_value >> 8) & 0xFF,
                                        b=rgb_value & 0xFF,
                                    )
                                )
                        return pixels
                except ValueError:
                    continue

    async def receive_stats(self) -> Stats:
        """Wait for and parse stats response."""
        while True:
            data = await self.receive()
            if isinstance(data, bytes) and len(data) > 0:
                try:
                    response_type = ResponseType(data[0])
                    if response_type == ResponseType.STATS:
                        # Parse stats message: [type:1][client_count:2][rps:4] = 7 bytes
                        if len(data) >= 7:
                            client_count_bytes = data[1:3]
                            rps_bytes = data[3:7]

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

                        return Stats(connected_clients=0, requests_per_second=0.0)
                except ValueError:
                    continue

    async def listen_for_messages(self):
        """
        Continuously listens for messages and yields them as they arrive.
        """
        try:
            while self.is_connected:
                data = await self.receive()
                if isinstance(data, bytes) and len(data) > 0:
                    try:
                        response_type = ResponseType(data[0])
                        yield response_type, data[1:]
                    except ValueError:
                        continue
        except Exception:
            return

    async def wait_for_response_type(
        self, expected_type: ResponseType, timeout: float = 5.0
    ):
        """
        Block until a specific response type is received, with timeout.
        """
        try:
            return await asyncio.wait_for(
                self._wait_for_type(expected_type), timeout=timeout
            )
        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Timeout waiting for {expected_type}") from e

    async def _wait_for_type(self, expected_type: ResponseType):
        """Helper method for waiting for a specific response type."""
        async for response_type, data in self.listen_for_messages():
            if response_type == expected_type:
                return data
