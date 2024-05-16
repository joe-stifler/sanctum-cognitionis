from notion_indexer.page_node import PageNode
from notion_indexer.notion_node import NotionNode
from notion_indexer.database_node import DatabaseNode
from notion_indexer.block_node import BlockNode, BlockFactory, ChildDatabaseBlock, ChildPageBlock

from uuid import UUID
from urllib.parse import urlparse
from notion_client import Client
from typing import List, Union
from notion_client.helpers import collect_paginated_api, iterate_paginated_api

class NotionClient:
    """A client for interacting with Notion."""

    def __init__(self, integration_token: str):
        """Initializes the Notion client with an integration token."""
        self.client = Client(auth=integration_token)

    def get_id(self, url: str) -> str:
        """Return the id of the object behind the given URL."""
        parsed = urlparse(url)

        if parsed.netloc not in ("notion.so", "www.notion.so"):
            raise ValueError("Not a valid Notion URL.")

        path = parsed.path

        if len(path) < 32:
            raise ValueError("The path in the URL seems to be incorrect.")
        raw_id = path[-32:]
        
        if len(parsed.fragment) == 32:
            raw_id = parsed.fragment

        return str(UUID(raw_id))

    def get_block_children(self, block_id: str) -> List[BlockNode]:
        """Retrieves the children blocks of a given block.

        Args:
            block_id: The ID of the block.

        Returns:
            A list of BlockNode objects representing the children blocks.
        """
        children_data = collect_paginated_api(
            self.client.blocks.children.list,
            block_id=block_id
        )
        return [BlockFactory.create_block(child_data) for child_data in children_data]

    def get_block(self, block_id: str) -> BlockNode:
        """Retrieves a Notion block.

        Args:
            block_id (str): The ID of the block.

        Returns:
            BlockNode: The retrieved Notion block.
        """
        return BlockFactory.create_block(self.client.blocks.retrieve(block_id))

    def get_page(self, page_id: str) -> PageNode:
        """Retrieves a Notion page.

        Args:
            page_id (str): The ID of the page.

        Returns:
            PageNode: The retrieved Notion page.
        """
        return PageNode(**self.client.pages.retrieve(page_id))

    def get_database(self, database_id: str, **kwargs) -> DatabaseNode:
        """Retrieves a Notion database.

        Args:
            database_id (str): The ID of the database.

        Returns:
            DatabaseNode: The retrieved Notion database.
        """
        database_data = self.client.databases.retrieve(database_id)
        for key in kwargs:
            if key in database_data:
                raise ValueError(f"Key {key} not present in database_data")
        database_data.update(kwargs)
        return DatabaseNode(**database_data)

    def get_database_pages(self, database_id: str, **kwargs) -> List[PageNode]:
        """Retrieves pages from a Notion database.

        Args:
            database_id (str): The ID of the database.

        Returns:
            List[PageNode]: A list of pages in the database.
        """

        pages_data = iterate_paginated_api(
            self.client.databases.query,
            database_id=database_id,
            **kwargs
        )
        collected_pages = []
        for iter, page_data in enumerate(pages_data):
            collected_pages.append(PageNode(**page_data))
            if "page_size" in kwargs and iter + 1 >= kwargs["page_size"]:
                break

        return collected_pages

    def fetch_children(self, node: Union[BlockNode, PageNode, DatabaseNode]):
        if isinstance(node, ChildPageBlock):
            node.children = [self.get_page(node.id), ]
        elif isinstance(node, ChildDatabaseBlock):
            node.children = [self.get_database(node.id), ]
        elif isinstance(node, DatabaseNode):
            node.children = self.get_database_pages(
                node.id,
                **node.get_kwargs()
            )
        else:
            node.children = self.get_block_children(node.id)

    def get_notion_object(self, url: str, **kwargs) -> NotionNode:
        """Identify if the URL is a database, a page, or a block."""
        id = self.get_id(url)

        get_methods = [
            lambda id: self.get_database(id, **kwargs),
            self.get_page,
            self.get_block
        ]

        for get_method in get_methods:
            try:
                node = get_method(id)
                return node
            except Exception as e:
                pass

        raise ValueError(f"No Notion object found for URL: {url}")
