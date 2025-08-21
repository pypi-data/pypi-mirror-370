import tempfile
from enum import StrEnum

from .browser import MERMAID_TEMPLATE, render_html
from .chunker import chunker
from .link import Link
from .node import Node


class Orientation(StrEnum):
    default = ""
    top_to_bottom = "TB"
    top_down = "TD"
    bottom_to_top = "BT"
    right_to_left = "RL"
    left_to_right = "LR"


class MermaidDiagram:
    title: str = ""
    nodes: list[Node]
    links: list[Link]
    orientation: Orientation

    def __init__(
        self,
        nodes: list[Node],
        links: list[Link],
        title: str = "",
        orientation: Orientation = Orientation.default,
    ) -> None:
        self.title = title
        self.nodes = nodes
        self.links = list(
            set(links)
        )  # no longer will duplicate links with the same ID cause duplicate links in the chart
        self.orientation = orientation

    def to_markdown(self) -> str:
        node_text = "\n".join(node.to_markdown() for node in sorted(self.nodes))
        link_text = "\n".join(link.to_markdown() for link in sorted(self.links))
        header = f"---\ntitle: {self.title}\n---" if self.title else ""
        graph_defines = f"graph {self.orientation}"
        return f"{header}\n{graph_defines}\n{node_text}\n{link_text}"

    def show(self) -> None:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", delete=False
        ) as f:  # delete=False needed to let the renderer actually find the file
            f.write(MERMAID_TEMPLATE.render(mermaid_markdown=self.to_markdown()))
            render_html(f.name)

    def chunk(self, split_nodes: list["Node"]) -> list["MermaidDiagram"]:
        return chunker(self.nodes, self.links, split_nodes)
