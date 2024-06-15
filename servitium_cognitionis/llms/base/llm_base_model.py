from abc import ABC, abstractmethod


class LLMBaseModel(ABC):
    def __init__(
        self,
        model_name,
        temperature,
        temperature_range,
    ):
        self._model_name = model_name
        self._temperature = temperature
        self._temperature_range = temperature_range

    def __str__(self) -> str:
        return self._model_name

    @property
    def name(self):
        return self._model_name

    @property
    def temperature_range(self):
        return self._temperature_range

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if value < self._temperature_range[0] or value > self._temperature_range[1]:
            raise ValueError(
                f"Temperature must be between {self._temperature_range[0]} and {self._temperature_range[1]}"
            )
        self._temperature = value

    # make hte following method abstract
    @abstractmethod
    def initialize_model(self, system_instruction=[], temperature=1.0):
        pass

    @abstractmethod
    def check_chat_session_exists(self, session_id):
        pass

    @abstractmethod
    def create_chat(self, session_id):
        pass

    @abstractmethod
    def send_stream_chat_message(
        self, session_id, message, system_message=None, files=[]
    ):
        pass
