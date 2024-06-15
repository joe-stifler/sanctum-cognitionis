from servitium_cognitionis.notion_indexer.notion_node import NotionNode
from servitium_cognitionis.notion_indexer.common_objects import RichText, PageProperty

import pandas as pd
from pydantic import Field
from typing import Dict, List, Any, Optional


class DatabaseNode(NotionNode):
    is_inline: bool = False
    title: List[RichText]
    properties: Dict[str, PageProperty] = {}
    page_size: Optional[int] = None
    filter: Optional[Dict[str, Any]] = None
    sorts: List[Dict[str, str]] = Field(default_factory=list)

    def get_kwargs(self):
        kwargs = {}
        if self.filter:
            kwargs["filter"] = self.filter
        if self.sorts:
            kwargs["sorts"] = self.sorts
        if self.page_size:
            kwargs["page_size"] = self.page_size
        return kwargs

    def to_dataframe(self) -> pd.DataFrame:
        """Convert the database to a Pandas DataFrame."""
        formatted_rows = {}
        for page in self.children:
            row = page.properties.copy()
            for property_name, property_data in row.items():
                formatted_prop_name = f"{property_name} ({property_data.type})"
                if formatted_prop_name not in formatted_rows:
                    formatted_rows[formatted_prop_name] = []
                formatted_rows[formatted_prop_name].append(property_data.get_value())

        return pd.DataFrame(formatted_rows)

    def to_markdown(self) -> str:
        markdown = self.to_dataframe().to_markdown() + "\n"
        children_markdown = ""
        for child in self.children:
            if len(child.children) == 0:
                continue # Skip empty pages
            children_markdown += child.to_markdown() + "\n"
        title = ''.join([rt.plain_text for rt in self.title])
        markdown =  f"<details><summary><h1>Database: {title}</h1></summary>\n\n" + markdown + "\n---\n" + children_markdown + "\n\n</details>\n"

        return markdown
