from dataclasses import dataclass, field


@dataclass
class Stats:
    """Represents statistics for the canvas."""

    connected_clients: int = field(
        default=0, metadata={"description": "Number of connected clients"}
    )
    requests_per_second: float = field(
        default=0.0, metadata={"description": "Average messages sent per second"}
    )

    def __repr__(self) -> str:
        """String representation of the stats."""
        return (
            f"Stats(connected_clients={self.connected_clients}, "
            f"requests_per_second={self.requests_per_second:.2f})"
        )

    def __str__(self) -> str:
        """String representation of the stats."""
        return (
            f"Connected Clients: {self.connected_clients}, "
            f"Requests per Second: {self.requests_per_second:.2f}"
        )
