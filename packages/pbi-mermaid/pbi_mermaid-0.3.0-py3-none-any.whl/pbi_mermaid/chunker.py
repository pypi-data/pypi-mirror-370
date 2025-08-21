from typing import TYPE_CHECKING

from .link import Link
from .node import Node

if TYPE_CHECKING:
    from .diagram import MermaidDiagram


def get_children(
    nodes: list["Node"], links: list["Link"], parent: "Node"
) -> tuple[set["Node"], set["Link"]]:
    c_nodes = {parent}
    c_links = set()
    while True:
        new_children = set()
        for link in links:
            if link.from_node in c_nodes:
                new_children.add(link.to_node)
                c_links.add(link)
        if not (new_children - c_nodes):
            break
        c_nodes |= new_children
    return c_nodes, c_links


def get_remaining(
    nodes: list["Node"], links: list["Link"], split_node: "Node"
) -> tuple[list["Node"], list["Link"]]:
    starting_nodes = {l.from_node for l in links if l.to_node == split_node}
    starting_links = set()

    remaining_links = {link for link in links if link.from_node != split_node}

    while True:
        new_nodes = set()
        new_links = set()
        for link in remaining_links:
            if link.from_node in starting_nodes:
                new_nodes.add(link.to_node)
                new_links.add(link)
            elif link.to_node in starting_nodes:
                new_nodes.add(link.from_node)
                new_links.add(link)
        if not (new_nodes - starting_nodes):
            break
        starting_nodes |= new_nodes
        starting_links |= new_links
        remaining_links -= new_links

    new_split_node = Node(
        id=split_node.id,
        shape=split_node.shape,
        content=split_node.content,
        style=split_node.style | {"stroke": "#ff0000", "stroke-width": "1px"},
    )
    ret_nodes = [n if n.id != split_node.id else new_split_node for n in starting_nodes]
    ret_links = []
    for link in starting_links:
        if link.from_node == split_node:
            new_link = Link(new_split_node, link.to_node)
            ret_links.append(new_link)
        elif link.to_node == split_node:
            new_link = Link(link.from_node, new_split_node)
            ret_links.append(new_link)
        else:
            ret_links.append(link)

    return ret_nodes, ret_links


def chunk_on_node(
    nodes: list["Node"], links: list["Link"], split_node: "Node"
) -> tuple["MermaidDiagram", list["Node"], list["Link"]]:
    from .diagram import MermaidDiagram

    children_nodes, children_links = get_children(nodes, links, split_node)
    diagram = MermaidDiagram(
        list(children_nodes), list(children_links), title=split_node.id
    )
    remaining_nodes, remaining_links = get_remaining(nodes, links, split_node)
    return diagram, list(remaining_nodes), list(remaining_links)


def chunker(
    nodes: list["Node"], links: list["Link"], split_nodes: list["Node"]
) -> list["MermaidDiagram"]:
    """

    Note: Order matters for the split nodes
    """
    from .diagram import MermaidDiagram

    diagrams = []
    for split_node in split_nodes:
        diagram, nodes, links = chunk_on_node(nodes, links, split_node)
        diagrams.append(diagram)
    diagrams.append(MermaidDiagram(nodes, links, title="ERD"))
    return diagrams
