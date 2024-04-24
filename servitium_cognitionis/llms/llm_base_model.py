from vertexai import generative_models
from vertexai.generative_models import GenerativeModel

class LLMBaseModel():
    def __init__(self, model_name, temperature, temperature_range, max_output_tokens, output_tokens_range):
        self._model_name = model_name
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._temperature_range = temperature_range
        self._output_tokens_range = output_tokens_range

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
            raise ValueError(f"Temperature must be between {self._temperature_range[0]} and {self._temperature_range[1]}")
        self._temperature = value

    @property
    def output_tokens_range(self):
        return self._output_tokens_range

    @property
    def max_output_tokens(self):
        return self._max_output_tokens

    @max_output_tokens.setter
    def max_output_tokens(self, value):
        if value < self._output_tokens_range[0] or value > self._output_tokens_range[1]:
            raise ValueError(f"Max output tokens must be between {self._output_tokens_range[0]} and {self._output_tokens_range[1]}")
        self._max_output_tokens = value

    def create_model(self):
        return GenerativeModel(
            model_name=self.name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens
            },
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        )
