from datetime import datetime
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from typing import Optional, Dict, Literal, List, Union, Any

class RichText(BaseModel):
    type: str 
    plain_text: str
    annotations: Optional[Dict] = None
    href: Optional[str] = None

@dataclass
class NotionUser(BaseModel):
    object: str = "user"
    id: str

@dataclass
class Parent(BaseModel):
    type: str
    database_id: Optional[str] = None
    page_id: Optional[str] = None
    workspace: Optional[bool] = None
    block_id: Optional[str] = None

@dataclass
class FileObject(BaseModel):
    type: Optional[str] = None
    url: Optional[str] = None
    expiry_time: Optional[datetime] = None

    def to_string(self):
        return f"[{self.url}:expire_type:{self.expiry_time}]({self.url})"

@dataclass
class EmojiObject(BaseModel):
    type: Literal["emoji"]
    emoji: str

class PageTitle(BaseModel):
    type: Literal["title"] = Field(..., alias='type')
    title: List[RichText] # Assuming title is always a list of rich text objects

    def to_markdown(self) -> str:
        return f"# {''.join([rt.plain_text for rt in self.title])} \n---\n"

class PageProperty(BaseModel):
    id: Optional[str] = None
    type: str
    name: Optional[str] = ""
    description: Optional[str] = ""
    title: Optional[Union[Dict, List[RichText], None]] = None
    checkbox: Optional[Union[Dict, bool]] = None
    created_by: Optional[Dict] = None
    created_time: Optional[Union[Dict, str]] = None
    date: Optional[Union[Dict, Any]] = None
    email: Optional[Union[Dict, str]] = None
    files: Optional[Union[Dict, List[FileObject]]] = None
    formula: Optional[Union[Dict, Any]] = None
    last_edited_by: Optional[Dict] = None
    last_edited_time: Optional[Union[Dict, str]] = None
    multi_select: Optional[Union[List, Dict, None]] = None
    number: Optional[Union[Dict, float]] = None
    people: Optional[Union[Dict, List[NotionUser]]] = None
    phone_number: Optional[Union[Dict, str]] = None
    relation: Optional[Union[Dict, List[Dict]]] = None
    rich_text: Optional[Union[Dict, List[RichText]]] = None
    rollup: Optional[Union[Dict, Any]] = None
    select: Optional[Union[Dict, str]] = None
    status: Optional[Union[Dict, str]] = None
    url: Optional[Union[Dict, str]] = None

    def get_value(self):
        """Returns the formatted value of the property based on its type."""
        property_type = self.type

        if property_type == "checkbox":
            if isinstance(self.checkbox, dict):
                return False
            else:
                return self.checkbox
        elif property_type == "created_by":
            return self.created_by.get("id", None) if self.created_by else None
        elif property_type == "created_time":
            created_time_str = self.created_time.get("start") if isinstance(self.created_time, dict) else self.created_time
            return datetime.fromisoformat(created_time_str[:-1] + '+00:00') if created_time_str else None
        elif property_type == "date":
            date_str = self.date.get("start") if isinstance(self.date, dict) else self.date
            return date_str
        elif property_type == "email":
            return self.email.get("email", None) if isinstance(self.email, dict) else self.email
        elif property_type == "files":
            if isinstance(self.files, dict):
                return [file.get("file", {}).get("url", None) for file in self.files.get("files", [])]
            
            if isinstance(self.files, list):
                return [file.to_string() for file in self.files]

        elif property_type == "formula":
            formula_type = self.formula.get('type', None)
            return self.formula.get(formula_type, None) if formula_type else None
        elif property_type == "last_edited_by":
            return self.last_edited_by.get("id", None) if self.last_edited_by else None
        elif property_type == "last_edited_time":
            last_edited_time_str = self.last_edited_time.get("start") if isinstance(self.last_edited_time, dict) else self.last_edited_time
            return datetime.fromisoformat(last_edited_time_str[:-1] + '+00:00') if last_edited_time_str else None
        elif property_type == "multi_select":
            if isinstance(self.multi_select, list):
                return [option.get('name') for option in self.multi_select]
            elif isinstance(self.multi_select, dict):
                return [option.get('name') for option in self.multi_select.get('options', [])]
            else:
                return None
        elif property_type == "number":
            return float(self.number) if isinstance(self.number, dict) else self.number
        elif property_type == "people":
            if isinstance(self.people, dict):
                return []

            # else it's a list of personuser
            return [person.id for person in self.people]
        elif property_type == "phone_number":
            return self.phone_number.phone_number.get("phone_number", None) if isinstance(self.phone_number, dict) else self.phone_number
        elif property_type == "relation":
            return [relation.get("id", None) for relation in self.relation] if isinstance(self.relation, dict) else self.relation
        elif property_type == "rich_text":
            return "".join([rt.plain_text for rt in self.rich_text])
        elif property_type == "rollup":
            rollup_type = self.rollup.get('type', None)
            return self.rollup.get(rollup_type, None) if rollup_type else None
        elif property_type == "select":
            return self.select.get("name", None) if isinstance(self.select, dict) else self.select
        elif property_type == "status":
            return self.status.get("name", None) if isinstance(self.status, dict) else self.status
        elif property_type == "title":
            return ''.join([rt.plain_text for rt in self.title]) if self.title else ""
        elif property_type == "url":
            return self.url.get("url", None) if isinstance(self.url, dict) else self.url
        else:
            return None

