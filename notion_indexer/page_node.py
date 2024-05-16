from notion_indexer.notion_node import NotionNode
from notion_indexer.common_objects import PageTitle, FileObject, EmojiObject, PageProperty

from typing import Optional, Dict, Any, Union

class PageNode(NotionNode):
    """Represents a Notion page."""
    cover: Optional[FileObject] = None
    properties: Dict[str, PageProperty] = {}
    icon: Optional[Union[FileObject, EmojiObject]] = None

    def title(self) -> str:
        """Get the title of the page."""
        # find the property in properties that have a PageProperty object of type `title`
        for _prop_name, prop_value in self.properties.items():
            if prop_value.type == "title":
                title = prop_value.title
                page_title = ''.join([rt.plain_text for rt in title]) if title else ""
                return page_title
        return ""

    def to_markdown(self) -> str:
        """Convert the page to markdown format."""
        # iterate through the properties and find the one of type `title`
        markdown = "<details><summary>Page Properties:</summary>\n\n"

        for prop_name, prop_value in self.properties.items():
            markdown += f"* {prop_name}: {prop_value.get_value()}\n\n"

        markdown += f"* ID: {self.id}\n\n"
        markdown += f"* Url: {self.url}\n\n"
        markdown += f"* Created Time: {self.created_time}\n\n"
        markdown += f"* Last Edited Time: {self.last_edited_time}\n\n"
        markdown += f"* Created By: {self.created_by}\n\n"
        markdown += f"* Last Edited By: {self.last_edited_by}\n\n"
        markdown += f"* In Trash: {self.in_trash}\n\n"
        markdown += f"* Archived: {self.archived}\n\n"
        markdown += f"* Object: {self.object}\n\n"
        markdown += f"* Request ID: {self.request_id}\n\n"
        markdown += f"* Has Children: {self.has_children}\n\n"
        markdown += f"* Parent: {self.parent}\n\n"

        markdown += "</details>\n\n"

        for child in self.children:
            markdown += child.to_markdown() + "\n"

        # surround the markdown with a details tag, having the title as H1
        markdown = f"<details><summary><b>Page: {self.title()}</b></summary>\n\n" + markdown + "\n\n</details>\n"

        return markdown
