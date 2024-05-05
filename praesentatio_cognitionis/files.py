import json
from io import BytesIO
from abc import ABC, abstractmethod

class BaseFile(ABC):
    """Abstract base class for processed files."""

    def __init__(self, name, content, mime_type, media_type):
        self._name = name
        self._content = content
        self._mime_type = mime_type
        self._media_type = media_type

    @property
    def name(self):
        return self._name

    @property
    def content(self):
        return self._content

    @property
    def mime_type(self):
        return self._mime_type

    @property
    def file_type(self):
        assert "/" in self.mime_type, "Invalid mime type"
        return self.mime_type.split("/")[1]

    @property
    def media_type(self):
        return self._media_type

    @abstractmethod
    def get_content_as_bytes(self):
        """Returns the content as bytes (abstract method)."""
        pass

class PandasFile(BaseFile):
    """Represents a Pandas DataFrame file."""
    SUPPORTED_TYPES = {
        "csv": "text/plain",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "text/plain", "tabular_data")

    def get_content_as_bytes(self):
        return self.content.to_csv(index=False).encode('utf-8')

class PDFFile(BaseFile):
    """Represents a PDF file."""
    SUPPORTED_TYPES = {
        "pdf": "application/pdf",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "application/pdf", "pdf")

    def get_content_as_bytes(self):
        return self.content

class AudioFile(BaseFile):
    """Represents an audio file."""
    SUPPORTED_TYPES = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }

    def __init__(self, name, content, extension):
        mime_type = AudioFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "audio")

    def get_content_as_bytes(self):
        return self.content

class ImageFile(BaseFile):
    """Represents an image file."""
    SUPPORTED_TYPES = {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "gif": "image/gif",
    }

    def __init__(self, name, content, extension):
        mime_type = ImageFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "image")

    def get_content_as_bytes(self):
        img_byte_arr = BytesIO()
        self.content.save(img_byte_arr, format=self.file_type.upper())
        return img_byte_arr.getvalue()

class TextFile(BaseFile):
    """Represents a text file."""
    SUPPORTED_TYPES = {
        "txt": "text/plain",
        "md": "text/markdown",
        "srt": "text/plain",
    }

    def __init__(self, name, content, extension):
        mime_type = TextFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "text")

    def get_content_as_bytes(self):
        return self.content.encode('utf-8')

class JsonFile(BaseFile):
    """Represents a JSON file."""
    SUPPORTED_TYPES = {
        "json": "application/json",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "text/plain", "text")

    def get_content_as_bytes(self):
        return json.dumps(self.content).encode('utf-8')

class CodeFile(BaseFile):
    """Represents a code file."""
    SUPPORTED_TYPES = {
        "py": "text/plain",
        "cpp": "text/plain",
        "c": "text/plain",
        "h": "text/plain",
        "hpp": "text/plain",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "text/plain", "code")

        self._language = ""

        if self.file_type == "py":
            self._language = "python"
        elif self.file_type in ["c", "h"]:
            self._language = "c"
        elif self.file_type in ["cpp", "hpp"]:
            self._language = "cpp"
        else:
            raise ValueError(f"Unsupported code file type: {self.file_type}")

    def get_content_as_bytes(self):
        return self.content.encode('utf-8')

    @property
    def language(self):
        return self._language
