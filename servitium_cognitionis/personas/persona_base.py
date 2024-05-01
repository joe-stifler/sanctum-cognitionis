import json
from datetime import datetime

class Persona:
    def __init__(self, persona_data):
        self._name = persona_data.get('name', '')
        self._avatar = "👩🏽‍🏫"
        self._knowledge_files = persona_data.get('knowledge', [])
        self._thought_process = persona_data.get('thought_process', None)
        self._creativity_level = persona_data.get('creativity_level', None)
        self._speech_conciseness = persona_data.get('speech_conciseness', None)
        self._thinking_style = persona_data.get('thinking_style', 'LLMMockFamily')
        self._persona_description_file = persona_data.get('persona_description', '')

    @property
    def name(self):
        return self._name

    @property
    def avatar(self):
        return self._avatar

    @property
    def thinking_style(self):
        return self._thinking_style

    @property
    def speech_conciseness(self):
        return self._speech_conciseness

    @property
    def knowledge_files(self):
        return self._knowledge_files

    @property
    def thought_process(self):
        return self._thought_process

    @property
    def creativity_level(self):
        return self._creativity_level

    def convert_files_to_str(self, files_path):
        files_content = "## Arquivos disponíveis na base de conhecimento do professor(a):\n\n"
        files_content += "--------------------------------------------------------\n\n"
        
        for file_path in files_path:
            files_content += f"### Conteúdo do arquivo `{file_path}`:\n\n"
            
            extension = file_path.split(".")[-1]
            try:
                with open(file_path, "r", encoding='utf-8') as file:
                    files_content += f"```{extension}\n" + file.read() + "\n```\n\n"
            except FileNotFoundError:
                files_content += "Arquivo não encontrado.\n\n"
        
        return files_content

    def read_description(self):
        try:
            with open(self._persona_description_file, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Description file not found."

    def present_initial_state(self):
        files_str = self.convert_files_to_str(self._knowledge_files)
        description = self.read_description()
        return f"{files_str}\n---\n\n{description}"

    def __str__(self):
        return (
            f"Name: {self._name}\n"
            f"Avatar: {self._avatar}\n"
            f"Thinking Style: {self._thinking_style}\n"
            f"Speech Conciseness: {self._speech_conciseness}\n"
            f"Knowledge Files: {self._knowledge_files}\n"
            f"Thought Process: {self._thought_process}\n"
            f"Creativity Level: {self._creativity_level}\n"
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
        try:
            with open(path, 'r', encoding='utf-8') as file:
                persona_data = json.load(file)
                return cls(persona_data)
        except FileNotFoundError:
            print("The specified file was not found.")
            return None
        except json.JSONDecodeError:
            print("Error decoding the JSON data.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
