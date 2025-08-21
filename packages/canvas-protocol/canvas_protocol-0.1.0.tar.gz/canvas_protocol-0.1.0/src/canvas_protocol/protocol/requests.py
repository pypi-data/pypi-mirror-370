from enum import Enum


class RequestType(Enum):
    """ALl request types sent by the client to the server."""

    SET_PIXEL = 1
    GET_PIXEL = 2
    GET_ALL_PIXELS = 3
    GET_STATS = 4
