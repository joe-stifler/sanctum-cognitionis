from praesentatio_cognitionis.files import PandasFile, PDFFile, AudioFile, ImageFile

from PIL import Image
from io import BytesIO
from pathlib import Path

class StreamlitFileHandler:
    SUPPORTED_FILE_TYPES = [
        # Image Files
        'png', 'jpg', '.jpeg', '.gif',

        # Text Files
        '.json', '.txt', '.md', '.srt', '.sub',
        
        # Tabular Data Files
        '.csv', '.xlsx', '.xls',
        
        # Code Files
        '.py', '.cpp', '.c', '.h', '.hpp',
        
        # Audio Files
        '.wav', '.mp3', '.ogg', '.flac',
        
        # PDF Files
        '.pdf'
    ]
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
        # elif suffix in ['.txt', '.md', '.srt', '.sub']:
        #     return TextFile(file.name, file.getvalue().decode('utf-8'))

        # elif suffix in ['.json']:
        #     return JSONFile(file.name, json.load(BytesIO(file.getvalue())))
        # elif suffix in ['.py', '.cpp', '.c', '.h', '.hpp']:
        #     return CodeFile(file.name, file.getvalue().decode('utf-8'))
        # elif suffix in ['.csv']:
        #     return PandasFile(file.name, pd.read_csv(BytesIO(file.getvalue())))
        # elif suffix in ['.xlsx', '.xls']:
        #     return PandasFile(file.name, pd.read_excel(BytesIO(file.getvalue())))
        # elif suffix in ['.wav', '.mp3', '.ogg', '.flac']:
        #     return AudioFile(file.name, file.getvalue(), suffix[1:]) # Extract extension without the dot
        # elif suffix in ['.mp4', '.mov']: 
        #     return VideoFile(file.name, file.getvalue(), suffix[1:]) # Extract extension without the dot
        else:
            raise Exception(f"Arquivo nao suportado: {suffix}")

    def process_files(self):
        """Processes uploaded files and returns a list of CustomFile objects."""
        processed_files = []
        for file in self.uploaded_files:
            if file:
                processed_files.append(self._convert_file(file))
        return processed_files
