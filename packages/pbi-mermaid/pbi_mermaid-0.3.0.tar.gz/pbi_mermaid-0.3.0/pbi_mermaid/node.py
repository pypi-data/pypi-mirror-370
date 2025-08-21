from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class Shape:
    start: str
    end: str


class NodeShape(Enum):
    normal = Shape("[", "]")
    round_edge = Shape("(", ")")
    stadium_shape = Shape("([", "])")
    subroutine_shape = Shape("[[", "]]")
    cylindrical = Shape("[(", ")]")
    circle = Shape("((", "))")
    label_shape = Shape(">", "]")
    rhombus = Shape("{", "}")
    hexagon = Shape("{{", "}}")
    parallelogram = Shape("[/", "/]")
    parallelogram_alt = Shape("[\\", "\\]")
    trapezoid = Shape("[/", "\\]")
    trapezoid_alt = Shape("[\\", "/]")
    double_circle = Shape("(((", ")))")


class Node:
    id: str
    shape: NodeShape
    content: str
    style: dict[str, str]

    def __init__(
        self,
        id: str,
        shape: NodeShape = NodeShape.normal,
        content: str = "",
        style: dict[str, str] | None = None,
    ) -> None:
        self.id = id
        self.shape = shape
        self.content = content
        self.style = style or {}

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.id < other.id

    def escape_content(self) -> None:
        self.content = f'"{self.content}"'

    def to_markdown(self) -> str:
        ret = f"{self.id}{self.shape.value.start}{self.content or self.id}{self.shape.value.end}"
        if self.style:
            style = ",".join(f"{k}:{v}" for k, v in self.style.items())
            ret += f"\nstyle {self.id} {style}"
        return ret

    def __repr__(self) -> str:
        return f"Node({self.id})"
