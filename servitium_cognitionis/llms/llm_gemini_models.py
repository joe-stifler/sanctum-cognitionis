from .llm_base_model import LLMBaseModel

from enum import Enum


class LLMGeminiModel1_5Pro(LLMBaseModel):
    def __init__(self, temperature=0.86, max_output_tokens=8192):
        super().__init__(
            "gemini-1.5-pro",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModel1_0Pro002(LLMBaseModel):
    def __init__(self, temperature=0.91, max_output_tokens=8192):
        super().__init__(
            "gemini-1.0-pro-002",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModelExperimental(LLMBaseModel):
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

    def __str__(self):
        return self.value.name
