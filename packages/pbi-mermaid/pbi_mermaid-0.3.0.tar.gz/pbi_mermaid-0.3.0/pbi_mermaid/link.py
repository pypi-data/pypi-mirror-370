from enum import StrEnum
from typing import Any

from .node import Node


class LinkShape(StrEnum):
    normal = "---"
    dotted = "-.-"
    thick = "==="


class LinkHead(StrEnum):
    none = ""
    arrow = ">"
    left_arrow = "<"
    bullet = "o"
    cross = "x"


class Link:
    from_node: Node
    to_node: Node
    id: str
    from_head: str
    to_head: str
    link_shape: LinkShape
    link_text: str | None

    def __init__(
        self,
        from_node: Node,
        to_node: Node,
        /,
        id: str | None = None,
        from_head: LinkHead = LinkHead.none,
        to_head: LinkHead = LinkHead.arrow,
        link_shape: LinkShape = LinkShape.normal,
        link_text: str | None = None,
    ) -> None:
        self.id = id or f"{from_node.id}-->{to_node.id}"
        self.from_node = from_node
        self.to_node = to_node
        self.from_head = from_head
        self.to_head = to_head
        self.link_shape = link_shape
        self.link_text = link_text

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Link):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Link):
            return NotImplemented
        return (self.from_head, self.to_head) < (other.from_head, other.to_head)

    def to_markdown(self) -> str:
        link_text = f"{self.from_head}{self.link_shape}{self.to_head}"
        if self.link_text:
            link_text += f"|{self.link_text}|"
        return f"{self.from_node.id} {link_text} {self.to_node.id}"

    def __repr__(self) -> str:
        return f"Link(from={self.from_node}, to={self.to_node})"
