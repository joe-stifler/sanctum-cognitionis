from servitium_cognitionis.notion_indexer.notion_client import NotionClient
from servitium_cognitionis.notion_indexer.notion_traverser import NotionTraverser

from typing import List, Optional, Any, Dict


class NotionReader:
    """Notion reader. Reads data from Notion pages and databases.

    Args:
        integration_token (str): Notion integration token.
        max_depth (int): Maximum depth to traverse the Notion tree, default -1 for no limit.
        exclude_nodes (Optional[List[str]]): List of node IDs to exclude during traversal.
    """

    def __init__(
        self,
        integration_token: Optional[str] = None,
    ) -> None:
        """Initialize with parameters."""
        self.notion_client = NotionClient(integration_token=integration_token)

    def load_data(self, url: str, max_depth: int = 1, **kwargs) -> Any:
        """Load data from a single Notion URL.

        Args:
            url (str): URL of the Notion page, database, or block to load.
            max_depth (int): Maximum depth to traverse the Notion tree, default -1 for no limit.
            query_filter: A Dict object if `url` is a database, otherwise None.
        """
        root_node = self.notion_client.get_notion_object(url, **kwargs)

        traverser = NotionTraverser(max_depth=max_depth)

        traverser.traverse(
            root_node,
            visit_function=lambda node: self.notion_client.fetch_children(node)
        )

        return root_node
