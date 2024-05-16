from notion_indexer.notion_node import NotionNode
from notion_indexer.common_objects import RichText, FileObject

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal, Union, Any
from notion_client.helpers import get_url
from pydantic.dataclasses import dataclass

# -------------------------------------
# Common Block Content and Base Classes
# -------------------------------------

@dataclass
class BlockContent(BaseModel):
    """Represents common content fields for various Notion blocks."""
    rich_text: Optional[List[RichText]] = Field(default_factory=list)
    color: Optional[str] = None
    icon: Optional[Dict] = None
    caption: Optional[List[RichText]] = Field(default_factory=list)
    url: Optional[str] = None
    checked: bool = False
    type: Optional[str] = None
    file: Optional[FileObject] = None
    external: Optional[FileObject] = None
    name: Optional[str] = None
    title: Optional[str] = None
    table_width: Optional[int] = None
    has_column_header: Optional[bool] = None
    has_row_header: Optional[bool] = None
    cells: Optional[List[List[RichText]]] = None
    language: Optional[str] = None
    synced_from: Optional[Dict[str, str]] = None
    is_toggleable: Optional[bool] = False

    def get_rich_text_content(self) -> str:
        """Extracts and joins the plain text from the rich_text list."""
        return "".join([rt.plain_text for rt in self.rich_text])


class BlockNode(NotionNode):
    """Represents a Notion block (base class)."""
    object: str = "block"
    id: str
    created_time: str
    last_edited_time: str
    has_children: bool
    archived: bool
    type: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_markdown(self) -> str:
        raise NotImplementedError("`to_markdown` method must be implemented in subclass")


# -------------------------------------
# Specific Block Type Classes
# -------------------------------------

class ParagraphBlock(BlockNode):
    type: Literal["paragraph"] = Field(..., alias='type')
    paragraph: BlockContent

    def to_markdown(self) -> str:
        return f"{self.paragraph.get_rich_text_content()}\n"


class HeadingBlock(BlockNode):
    def to_markdown(self, level: int, heading_content: BlockContent) -> str:
        content = heading_content.get_rich_text_content()
        markdown = f"{'#' * level} {content}\n"
        if heading_content.is_toggleable:
            markdown += f"\n<details>\n<summary>{content}</summary>\n\n"
            for child in self.children: 
                markdown += child.to_markdown() + "\n"
            markdown += "</details>\n\n"
        return markdown


class Heading1Block(HeadingBlock):
    type: Literal["heading_1"] = Field(..., alias='type')
    heading_1: BlockContent

    def to_markdown(self) -> str:
        return super().to_markdown(level=1, heading_content=self.heading_1)


class Heading2Block(HeadingBlock):
    type: Literal["heading_2"] = Field(..., alias='type')
    heading_2: BlockContent

    def to_markdown(self) -> str:
        return super().to_markdown(level=2, heading_content=self.heading_2)


class Heading3Block(HeadingBlock):
    type: Literal["heading_3"] = Field(..., alias='type')
    heading_3: BlockContent

    def to_markdown(self) -> str:
        return super().to_markdown(level=3, heading_content=self.heading_3)


class BulletedListItemBlock(BlockNode):
    type: Literal["bulleted_list_item"] = Field(..., alias='type')
    bulleted_list_item: BlockContent

    def to_markdown(self) -> str:
        markdown = f"- {self.bulleted_list_item.get_rich_text_content()}\n"
        for child in self.children:
            markdown += child.to_markdown() + "\n"
        return markdown


class NumberedListItemBlock(BlockNode):
    type: Literal["numbered_list_item"] = Field(..., alias='type')
    numbered_list_item: BlockContent

    def to_markdown(self) -> str:
        markdown = f"1. {self.numbered_list_item.get_rich_text_content()}\n"
        for child in self.children: 
            markdown += child.to_markdown() + "\n"
        return markdown


class ToDoBlock(BlockNode):
    type: Literal["to_do"] = Field(..., alias='type')
    to_do: BlockContent

    def to_markdown(self) -> str:
        markdown = f"- [{'x' if self.to_do.checked else ' '}] {self.to_do.get_rich_text_content()}\n"
        for child in self.children:
            markdown += child.to_markdown() + "\n"
        return markdown


class ToggleBlock(BlockNode):
    type: Literal["toggle"] = Field(..., alias='type')
    toggle: BlockContent

    def to_markdown(self) -> str:
        content = self.toggle.get_rich_text_content()
        markdown = f"\n<details>\n<summary>{content}</summary>\n\n"
        for child in self.children:
            markdown += child.to_markdown() + "\n"
        markdown += "</details>\n\n"
        return markdown


class ChildPageBlock(BlockNode):
    type: Literal["child_page"] = Field(..., alias='type')
    child_page: BlockContent

    def to_markdown(self) -> str:
        url = get_url(self.id)
        if not self.children:
            return f"[{self.child_page.title}]({url})\n"
        link = f'{self.child_page.title}'
        markdown = f"\n<details>\n<summary>{link}</summary>\n\n"
        for child in self.children:  
            markdown += child.to_markdown() + "\n"
        markdown += "</details>\n\n"
        return markdown


class ChildDatabaseBlock(BlockNode):
    type: Literal["child_database"] = Field(..., alias='type')
    child_database: BlockContent

    def to_markdown(self) -> str:
        url = get_url(self.id)
        if not self.children:
            return f"[{self.child_database.title}]({url})\n"
        link = f'{self.child_database.title}'
        markdown = f"\n<details>\n<summary>{link}</summary>\n\n"
        for child in self.children: 
            markdown += child.to_markdown() + "\n"
        markdown += "</details>\n\n"
        return markdown


class EmbedBlock(BlockNode):
    type: Literal["embed"] = Field(..., alias='type')
    embed: BlockContent

    def to_markdown(self) -> str:
        return f"[Embed: {self.embed.url}]({self.embed.url})\n"


# -------------------------------------
# Media Blocks 
# -------------------------------------

@dataclass
class MediaBlockContent:
    type: Optional[str] = ""
    file: Optional[FileObject] = None
    external: Optional[FileObject] = None
    caption: Optional[Union[Dict, List[RichText]]] = Field(default_factory=list)

    def get_url(self) -> str:
        if self.type == "external":
            return self.external.url
        elif self.type == "file":
            return self.file.url
        return ""

class ImageBlock(BlockNode):
    type: Literal["image"] = Field(..., alias='type')
    image: MediaBlockContent

    def to_markdown(self) -> str:
        caption_text = "".join([rt.plain_text for rt in self.image.caption])
        return f"![{caption_text}]({self.image.get_url()})\n"

class VideoBlock(BlockNode):
    type: Literal["video"] = Field(..., alias='type')
    video: MediaBlockContent

    def to_markdown(self) -> str:
        url = self.video.get_url()
        caption_text = "".join([rt.plain_text for rt in self.video.caption]) or url
        return f"[{caption_text}]({url})\n"

class FileBlock(BlockNode):
    type: Literal["file"] = Field(..., alias='type')
    file: MediaBlockContent

    def to_markdown(self) -> str:
        caption_text = "".join([rt.plain_text for rt in self.file.caption])
        return f"[{self.file.type or 'file'}: {caption_text}]({self.file.get_url()})\n"

class PDFBlock(BlockNode):
    type: Literal["pdf"] = Field(..., alias='type')
    pdf: MediaBlockContent

    def to_markdown(self) -> str:
        caption_text = "".join([rt.plain_text for rt in self.pdf.caption])
        return f"[PDF: {caption_text}]({self.pdf.get_url()})\n"

# -------------------------------------
# Other Blocks
# -------------------------------------

class QuoteBlock(BlockNode):
    type: Literal["quote"] = Field(..., alias='type')
    quote: BlockContent

    def to_markdown(self) -> str:
        markdown = f"> {self.quote.get_rich_text_content()}\n"
        for child in self.children:  # Accessing children from BlockNode
            markdown += child.to_markdown() + "\n"
        return markdown


class CalloutBlock(BlockNode):
    type: Literal["callout"] = Field(..., alias='type')
    callout: BlockContent

    def to_markdown(self) -> str:
        icon_text = f"{self.callout.icon.get('emoji', '')} " if self.callout.icon else ""
        content = self.callout.get_rich_text_content()
        markdown = f"> {icon_text}{content}\n"
        for child in self.children:
            markdown += child.to_markdown() + "\n"
        return markdown


class DividerBlock(BlockNode):
    type: Literal["divider"] = Field(..., alias='type')

    def to_markdown(self) -> str:
        return "---\n"


class TableBlock(BlockNode):
    type: Literal["table"] = Field(..., alias='type')
    table: BlockContent

    def to_markdown(self) -> str:
        markdown = ""
        for i, child in enumerate(self.children):
            if child.type == "table_row":
                markdown += child.to_markdown()
                if i == 0 and (self.table.has_column_header or self.table.has_row_header):
                    markdown += "|" + "---|" * self.table.table_width + "\n"
        return markdown


class ColumnBlock(BlockNode):
    type: Literal["column"] = Field(..., alias='type')
    column: BlockContent

    def to_markdown(self) -> str:
        markdown = ""
        for child in self.children:
            markdown += child.to_markdown() + "\n"
        return markdown


class ColumnListBlock(BlockNode):
    type: Literal["column_list"] = Field(..., alias='type')
    column_list: BlockContent

    def to_markdown(self) -> str:
        markdown = ""
        for child in self.children:  
            markdown += child.to_markdown() + "\n"
        return markdown


class LinkPreviewBlock(BlockNode):
    type: Literal["link_preview"] = Field(..., alias='type')
    link_preview: BlockContent

    def to_markdown(self) -> str:
        return f"[Link Preview: {self.link_preview.url}]({self.link_preview.url})\n"


class SyncedBlock(BlockNode):
    type: Literal["synced_block"] = Field(..., alias='type')
    synced_block: BlockContent

    def to_markdown(self) -> str:
        markdown = ""
        for child in self.children: 
            markdown += child.to_markdown() + "\n"
        return markdown


class TemplateBlock(BlockNode):
    type: Literal["template"] = Field(..., alias='type')
    template: BlockContent

    def to_markdown(self) -> str:
        markdown = f"**Template:** {self.template.get_rich_text_content()}\n"
        for child in self.children: 
            markdown += child.to_markdown() + "\n"
        return markdown


class BookmarkBlock(BlockNode):
    type: Literal["bookmark"] = Field(..., alias='type')
    bookmark: BlockContent

    def to_markdown(self) -> str:
        caption_text = "".join([rt.plain_text for rt in self.bookmark.caption])
        return f"[{caption_text}]({self.bookmark.url})\n"


class TableRowBlock(BlockNode):
    type: Literal["table_row"] = Field(..., alias='type')
    table_row: BlockContent

    def to_markdown(self) -> str:
        markdown = "|"
        for cell in self.table_row.cells:
            markdown += " " + "".join([text.plain_text for text in cell]) + " |"
        return markdown + "\n"


class CodeBlock(BlockNode):
    type: Literal["code"] = Field(..., alias='type')
    code: BlockContent

    def to_markdown(self) -> str:
        content = self.code.get_rich_text_content()
        caption = "".join([rt.plain_text for rt in self.code.caption])
        return f"```{self.code.language}\n{content}\n```\n{caption}\n"


class UnsupportedBlock(BlockNode):
    type: Literal["unsupported"] = Field(..., alias='type')

    def to_markdown(self) -> str:
        return "**Unsupported Block Type**\n"


# -------------------------------------
# Block Factory
# -------------------------------------

class BlockFactory(BaseModel):
    @classmethod
    def create_block(cls, block_data: Dict) -> "BlockNode":
        block_type_mapping = {
            "paragraph": ParagraphBlock,
            "code": CodeBlock,
            "heading_1": Heading1Block,
            "heading_2": Heading2Block,
            "heading_3": Heading3Block,
            "bulleted_list_item": BulletedListItemBlock,
            "numbered_list_item": NumberedListItemBlock,
            "to_do": ToDoBlock,
            "toggle": ToggleBlock,
            "child_page": ChildPageBlock,
            "child_database": ChildDatabaseBlock,
            "embed": EmbedBlock,
            "image": ImageBlock,
            "video": VideoBlock,
            "file": FileBlock,
            "pdf": PDFBlock,
            "quote": QuoteBlock,
            "callout": CalloutBlock,
            "divider": DividerBlock,
            "table": TableBlock,
            "column": ColumnBlock,
            "column_list": ColumnListBlock,
            "link_preview": LinkPreviewBlock,
            "synced_block": SyncedBlock,
            "template": TemplateBlock,
            "table_row": TableRowBlock,
            "bookmark": BookmarkBlock,
            "unsupported": UnsupportedBlock,
        }

        block_type = block_data.get('type')
        block_class = block_type_mapping.get(block_type)

        if block_class is None:
            raise ValueError(f"Unsupported block type: {block_type}")

        return block_class(**block_data)
