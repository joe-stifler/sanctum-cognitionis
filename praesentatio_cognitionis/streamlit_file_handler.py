import json
import pandas as pd
from PIL import Image
from io import BytesIO
from pathlib import Path

class StreamlitFileHandler:
    SUPPORTED_FILE_TYPES = [
        'png', 'jpg', '.jpeg', '.gif',
        '.json', '.txt', '.md', '.srt',
        '.csv', '.xlsx', '.xls',
        '.sub', '.py', '.cpp', '.c', '.h', '.hpp',
        '.pdf'
    ]
    def __init__(self, uploaded_files):
        self.uploaded_files = uploaded_files

    def convert_file(self, file, suffix):
        """Converte um arquivo Streamlit para um formato padrão baseado no tipo do arquivo."""
        if suffix in ['.png', '.jpg', '.jpeg', '.gif']:
            return "image", Image.open(BytesIO(file.getvalue()))
        elif suffix in ['.json']:
            return "json", json.load(BytesIO(file.getvalue()))
        elif suffix in ['.txt', '.md', '.srt', '.sub']:
            return "text", file.getvalue().decode('utf-8')
        elif suffix in ['.py', '.cpp', '.c', '.h', '.hpp', ]:
            return "code", file.getvalue().decode('utf-8')
        elif suffix in ['.csv']:
            return "pandas", pd.read_csv(BytesIO(file.getvalue()))
        elif suffix in ['.xlsx', '.xls']:
            return "pandas", pd.read_excel(BytesIO(file.getvalue()))
        elif suffix in ['.pdf']:
            return "pdf", file.getbuffer()

        raise Exception(f"Unsupported file format: {suffix}")

    def process_files(self):
        """Processa todos os arquivos carregados e retorna uma lista de tuplas (nome, conteúdo)."""
        processed_files = []
        for file in self.uploaded_files:
            if file is not None:
                suffix = Path(file.name).suffix.lower()
                file_type, content = self.convert_file(file, suffix)
                processed_files.append((file.name, content, file_type))
        return processed_files
