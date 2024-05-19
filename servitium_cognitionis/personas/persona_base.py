import json
from datetime import datetime

class Persona:
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', '')
        self._avatar = kwargs.get('avatar', '🤖')
        self._knowledge_files = kwargs.get('knowledge', [])
        self._thinking_process = kwargs.get('thinking_process', None)
        self._speech_conciseness = kwargs.get('speech_conciseness', None)
        self._persona_description_file = kwargs.get('persona_description_file', '')

    @property
    def name(self):
        return self._name

    @property
    def thinking_process(self):
        return self._thinking_process

    @property
    def avatar(self):
        return self._avatar

    @property
    def speech_conciseness(self):
        return self._speech_conciseness

    @property
    def knowledge_files(self):
        return self._knowledge_files

    def convert_files_to_str(self):
        if len(self._knowledge_files) == 0:
            return ""

        files_content = "## Arquivos disponíveis na base de conhecimento do professor(a):\n\n"
        files_content += "--------------------------------------------------------\n\n"

        for file_path in self._knowledge_files:
            files_content += f"### Conteúdo do arquivo `{file_path}`:\n\n"
            
            extension = file_path.split(".")[-1]
            try:
                with open(file_path, "r", encoding='utf-8') as file:
                    files_content += f"```{extension}\n" + file.read() + "\n```\n\n"
            except FileNotFoundError:
                files_content += "Arquivo não encontrado.\n\n"
        
        return files_content

    def read_description(self):
        if len(self._persona_description_file) == 0:
            return ""

        with open(self._persona_description_file, 'r', encoding='utf-8') as file:
            return file.read()

    def present_yourself(self):
        files_str = self.convert_files_to_str()
        return f"{files_str}\n---\n\n{self.read_description()}"

    def __str__(self):
        return (
            f"Name: {self._name}\n"
            f"Avatar: {self._avatar}\n"
            f"Knowledge Files: {self._knowledge_files}\n"
            f"Persona Description File: {self._persona_description_file}"
        )

    def append_initial_state_to_file(self, file_path):
        # Get current datetime
        now = datetime.now()
        timestamp = now.strftime("%A, %d of %B, %Y, %H:%M:%S")

        # Separator
        separator = "--------------------------------------------------------"

        # Get the initial state
        initial_state = self.present_initial_state()

        # Prepare content to append
        content_to_append = f"{separator}\n{timestamp}\n{separator}\n{initial_state}\n{separator}\n{timestamp}\n{separator}\n"

        # Append to the file
        with open(file_path, "a", encoding='utf-8') as file:
            file.write(content_to_append)

    @classmethod
    def from_json(cls, path):
        with open(path, 'r', encoding='utf-8') as file:
            persona_data = json.load(file)
            return cls(persona_data)
