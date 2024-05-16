from uuid import UUID
from urllib.parse import urlparse


def custom_get_id(url: str) -> str:
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
