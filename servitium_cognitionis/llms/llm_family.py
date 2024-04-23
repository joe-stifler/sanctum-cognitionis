from enum import Enum, auto

from servitium_cognitionis.llms import LLMGeminiFamily

class LLMFamily(Enum):
    VERTEXAI_GEMINI = LLMGeminiFamily()
    
    @staticmethod
    def available_families():
        return [family.value for family in LLMFamily]
