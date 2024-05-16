from notion_indexer.notion_node import NotionNode

from typing import Callable


class NotionTraverser:
    """Handles traversal logic for Notion data."""

    def __init__(self, max_depth: int = -1):
        self.max_depth = max_depth
        self.visited_node_ids = set()

    def traverse(self, node: NotionNode, visit_function: Callable[[NotionNode], None], current_depth: int = 0) -> None:
        """Performs Depth-First Search (DFS) traversal of a Notion tree."""
        if self.max_depth != -1 and current_depth >= self.max_depth:
            return

        node_pair = (node.object, node.id)
        if node_pair in self.visited_node_ids:
            return

        self.visited_node_ids.add(node_pair)
        visit_function(node)

        for child in node.children:
            self.traverse(child, visit_function, current_depth + 1)
