from dataclasses import dataclass, field


@dataclass
class Color:
    """Represents a color in RGB format."""

    r: int = field(default=0, metadata={"description": "Red component (0-255)"})
    g: int = field(default=0, metadata={"description": "Green component (0-255)"})
    b: int = field(default=0, metadata={"description": "Blue component (0-255)"})

    def to_int(self) -> int:
        """Convert RGB color to a single integer."""
        return (self.r << 16) | (self.g << 8) | self.b

    def __repr__(self) -> str:
        """String representation of the color."""
        return f"Color(r={self.r}, g={self.g}, b={self.b})"

    def __str__(self) -> str:
        """String representation of the color."""
        return f"RGB({self.r}, {self.g}, {self.b})"
