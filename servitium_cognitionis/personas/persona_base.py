import json
from datetime import datetime


class Persona:
    def __init__(self, **kwargs):
        self._name = kwargs.get("name", "")
        self._avatar = kwargs.get("avatar", "🤖")
        self._knowledge_files = kwargs.get("knowledge", [])
        self._beg_persona_content = kwargs.get("beg_persona_content", "")
        self._end_persona_content = kwargs.get("end_persona_content", "")
        self._speech_conciseness = kwargs.get("speech_conciseness", None)
        self._persona_description_file = kwargs.get("persona_description_file", "")

    @property
    def name(self):
        return self._name

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

        files_content = "## Files available in the persona knowledge:\n\n"
        files_content += "--------------------------------------------------------\n\n"

        for file_path in self._knowledge_files:
            files_content += f"### File Content `{file_path}`:\n\n"

            extension = file_path.split(".")[-1]
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    files_content += f"```{extension}\n" + file.read() + "\n```\n\n"
            except FileNotFoundError:
                files_content += "File not found.\n\n"

        return files_content

    def read_description(self):
        if len(self._persona_description_file) == 0:
            return ""

        with open(self._persona_description_file, "r", encoding="utf-8") as file:
            return file.read()

    def present_yourself(self):
        # Get current datetime
        now = datetime.now()
        timestamp = now.strftime("%A, %d of %B, %Y, %H:%M:%S")

        persona_presentation = (
            f"<current_date_time>{timestamp}</current_date_time>\n"
            + f"<persona_name>{self._name}</persona_name>\n"
            + f"<persona_avatar>{self._avatar}</persona_avatar>\n"
            + f"{self._beg_persona_content}\n"
            + self.read_description()
            + f"\n{self._end_persona_content}\n"
        )

        return persona_presentation

    def __str__(self):
        return (
            f"Name: {self._name}\n"
            f"Avatar: {self._avatar}\n"
            f"Knowledge Files: {self._knowledge_files}\n"
            f"Persona Description File: {self._persona_description_file}"
        )

    @classmethod
    def from_json(cls, path):
        with open(path, "r", encoding="utf-8") as file:
            persona_data = json.load(file)
            return cls(persona_data)
