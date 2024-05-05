from praesentatio_cognitionis.files import (
    PandasFile,
    JsonFile,
    PDFFile,
    AudioFile,
    ImageFile,
    TextFile,
    CodeFile
)

import json
import pandas as pd
from PIL import Image
from io import BytesIO
from pathlib import Path

class StreamlitFileHandler:
    SUPPORTED_FILE_TYPES = {
        **PandasFile.SUPPORTED_TYPES,
        **JsonFile.SUPPORTED_TYPES,
        **PDFFile.SUPPORTED_TYPES,
        **AudioFile.SUPPORTED_TYPES,
        **ImageFile.SUPPORTED_TYPES,
        **TextFile.SUPPORTED_TYPES
    }

    def __init__(self, uploaded_files):
        self.uploaded_files = uploaded_files

    def _convert_file(self, file):
        """Converts a file to a specialized file object based on its type."""
        suffix = Path(file.name).suffix.lower()

        assert len(suffix) > 1, "File has no suffix"
        suffix = suffix[1:]

        if suffix in ImageFile.SUPPORTED_TYPES:
            image = Image.open(BytesIO(file.getvalue()))
            return ImageFile(file.name, image, suffix)
        elif suffix in PDFFile.SUPPORTED_TYPES:
            return PDFFile(file.name, file.getvalue())
        elif suffix in TextFile.SUPPORTED_TYPES:
            return TextFile(file.name, file.getvalue().decode('utf-8'), suffix)
        elif suffix in AudioFile.SUPPORTED_TYPES:
            return AudioFile(file.name, file.getvalue(), suffix)
        elif suffix in JsonFile.SUPPORTED_TYPES:
            return JsonFile(file.name, json.loads(file.getvalue().decode('utf-8')))
        elif suffix in PandasFile.SUPPORTED_TYPES:
            return PandasFile(file.name, pd.read_csv(BytesIO(file.getvalue())))
        elif suffix in ['.py', '.cpp', '.c', '.h', '.hpp']:
            return CodeFile(file.name, file.getvalue().decode('utf-8'))

        # elif suffix in ['.mp4', '.mov']: 
        #     return VideoFile(file.name, file.getvalue(), suffix[1:]) # Extract extension without the dot
        
        raise ValueError(f"Unsupported file type: {suffix}")

    def process_files(self):
        """Processes uploaded files and returns a list of CustomFile objects."""
        processed_files = []
        for file in self.uploaded_files:
            if file:
                processed_files.append(self._convert_file(file))
        return processed_files
