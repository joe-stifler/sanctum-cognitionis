import ollama
import google.generativeai as genai
from abc import ABC, abstractmethod


class LLMBaseModel(ABC):

    def __init__(
        self,
        model_name,
        temperature,
        temperature_range,
        max_output_tokens,
        output_tokens_range,
        system_instruction="",
    ):
        self._model_name = model_name
        self._temperature = temperature
        self._max_output_tokens = max_output_tokens
        self._temperature_range = temperature_range
        self._output_tokens_range = output_tokens_range
        self._system_instruction = system_instruction

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

    @property
    def output_tokens_range(self):
        return self._output_tokens_range

    @property
    def max_output_tokens(self):
        return self._max_output_tokens

    @max_output_tokens.setter
    def max_output_tokens(self, value):
        if value < self._output_tokens_range[0] or value > self._output_tokens_range[1]:
            raise ValueError(
                f"Max output tokens must be between {self._output_tokens_range[0]} and {self._output_tokens_range[1]}"
            )
        self._max_output_tokens = value

    # make hte following method abstract
    @abstractmethod
    def send_stream_message(self, message):
        pass


class OllamaModel(LLMBaseModel):
    def __init__(
        self,
        model_name,
        temperature=0.7,
        temperature_range=(0.0, 2.0),
        max_output_tokens=1024,
        output_tokens_range=(1, 4096),
    ):
        super().__init__(
            model_name,
            temperature,
            temperature_range,
            max_output_tokens,
            output_tokens_range,
        )

    def send_stream_message(self, message):
        prompt = self._system_instruction + "\n" + message
        response_stream = ollama.chat(
            model=self.name,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        # Extract the message content from the generator response. Yield inside
        for chunk in response_stream:
            content = chunk["message"]["content"]
            yield content


class GeminiModel(LLMBaseModel):
    def __init__(
        self,
        model_name,
        api_key,
        temperature=0.7,
        temperature_range=(0.0, 2.0),
        max_output_tokens=1024,
        output_tokens_range=(1, 4096),
    ):
        super().__init__(
            model_name,
            temperature,
            temperature_range,
            max_output_tokens,
            output_tokens_range,
        )
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.name)

        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)

    def send_stream_message(self, message):
        prompt = self._system_instruction + "\n" + message
        response_stream = self.model.generate_content(prompt, stream=True)
        for chunk in response_stream:
            yield chunk.text
