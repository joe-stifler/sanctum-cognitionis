from enum import Enum, auto

from servitium_cognitionis.llms import LLMGeminiFamily

class LLMFamily(Enum):
    VERTEXAI_GEMINI = LLMGeminiFamily()

    def __str__(self):
        return str(self.value)
