from enum import Enum


class ResponseType(Enum):
    """All response types sent by the server to the client."""

    # Broadcast messages (sent when other clients make changes)
    SET_PIXEL_BROADCAST = 1

    # Response messages (sent in response to requests)
    PIXEL_COLOR = 10
    ERROR = 11
    GET_ALL_PIXELS = 12
    STATS = 13
