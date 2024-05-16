from .common_objects import NotionUser, Parent

import json
from datetime import datetime
from abc import ABC, abstractmethod
from pydantic import BaseModel, validator
from typing import List, Optional, Any

class NotionNode(ABC, BaseModel):
    """Base class for all Notion nodes."""
    id: str
    created_time: str
    last_edited_time: str
    created_by: NotionUser
    last_edited_by: NotionUser
    in_trash: bool = False
    archived: bool = False
    object: str = ""
    request_id: Optional[str] = None
    has_children: bool = False
    parent: Optional[Parent] = None
    children: Optional[List[Any]] = []

    url: str = ""
    public_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the node to a dictionary."""
        return self.dict()

    def to_json(self) -> str:
        """Convert the node to a JSON string."""
        return json.dumps(self.to_dict())

    @abstractmethod
    def to_markdown(self) -> str:
        """Convert the node to markdown format."""
        pass
