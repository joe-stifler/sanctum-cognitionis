import json
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image
import io
from abc import ABC, abstractmethod


def pdf_to_text(pdf_bytes):
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text


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

    def metadata_header(self):
        return f"`{self.name}`:\n\n"

    def begin_delimiter_content(self):
        return f"```{self.media_type}\n"

    def end_delimiter_content(self):
        return "\n```\n\n"


class PandasFile(BaseFile):
    """Represents a Pandas DataFrame file."""

    SUPPORTED_TYPES = {
        "csv": "text/plain",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "text/plain", "text")

    def get_content_as_bytes(self):
        return self.content.to_csv(index=False).encode("utf-8")


class PDFFile(BaseFile):
    """Represents a PDF file."""

    SUPPORTED_TYPES = {
        "pdf": "application/pdf",
    }

    def __init__(self, name, content):
        # Note: PDFs are converted to images because Gemini in lib
        # version 0.5.3 yields error 500 when PDFs are sent as blobs.
        # Check discussion here: https://www.googlecloudcommunity.com/gc/AI-ML/pdf-analysis-using-gemini-1-5-pro/td-p/737171
        super().__init__(name, content, "text/plain", "text")

    def get_content_as_bytes(self):
        return pdf_to_text(self.content).encode("utf-8")


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
        "json": "application/json",
        "html": "text/plain",
    }

    def __init__(self, name, content, extension):
        mime_type = TextFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "text")

    def get_content_as_bytes(self):
        return self.content.encode("utf-8")


class JsonFile(BaseFile):
    """Represents a JSON file."""

    SUPPORTED_TYPES = {
        # "json": "application/json",
    }

    def __init__(self, name, content):
        super().__init__(name, content, "text/plain", "text")

    def get_content_as_bytes(self):
        return json.dumps(self.content).encode("utf-8")


class CodeFile(BaseFile):
    """Represents a code file."""

    SUPPORTED_TYPES = {
        "py": "text/plain",
        "cpp": "text/plain",
        "c": "text/plain",
        "h": "text/plain",
        "hpp": "text/plain",
    }

    def __init__(self, name, content, suffix):
        super().__init__(name, content, "text/plain", "text")

        self._language = ""

        if suffix == "py":
            self._language = "python"
        elif suffix in ["c", "h"]:
            self._language = "c"
        elif suffix in ["cpp", "hpp"]:
            self._language = "cpp"
        else:
            raise ValueError(f"Unsupported code file type: {suffix}")

    def get_content_as_bytes(self):
        return self.content.encode("utf-8")

    @property
    def language(self):
        return self._language


class VideoFile(BaseFile):
    """Represents a video file."""

    SUPPORTED_TYPES = {
        "mp4": "video/mp4",
        "avi": "video/avi",
        "mov": "video/quicktime",
    }

    def __init__(self, name, content, extension):
        mime_type = VideoFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "video")

    def get_content_as_bytes(self):
        return self.content


class AudioFile(BaseFile):
    """Represents an audio file."""

    SUPPORTED_TYPES = {
        "mp3": "audio/mp3",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
    }

    def __init__(self, name, content, extension):
        mime_type = AudioFile.SUPPORTED_TYPES[extension]
        super().__init__(name, content, mime_type, "audio")

    def get_content_as_bytes(self):
        return self.content
