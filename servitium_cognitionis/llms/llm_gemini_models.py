from enum import Enum


class LLMGeminiModelBase():
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


class LLMGeminiModel1_5Pro(LLMGeminiModelBase):
    def __init__(self, temperature=0.86, max_output_tokens=8192):
        super().__init__(
            "gemini-1.5-pro",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModel1_0Pro002(LLMGeminiModelBase):
    def __init__(self, temperature=0.91, max_output_tokens=8192):
        super().__init__(
            "gemini-1.0-pro-002",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModelExperimental(LLMGeminiModelBase):
    def __init__(self, temperature=1.0, max_output_tokens=8192):
        super().__init__("gemini-experimental",
            temperature=temperature,
            temperature_range=(0.0, 1.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModels(Enum):
    GEMINI_1_5_PRO = LLMGeminiModel1_5Pro()
    GEMINI_1_0_PRO_002 = LLMGeminiModel1_0Pro002()
    GEMINI_EXPERIMENTAL = LLMGeminiModelExperimental()
    
    @staticmethod
    def available_models():
        return [family.value for family in LLMGeminiModels]
