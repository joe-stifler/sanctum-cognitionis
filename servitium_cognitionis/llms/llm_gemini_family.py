from servitium_cognitionis.llms import LLMBaseFamily, LLMGeminiModels, LLMBaseModel

from enum import Enum
from typing import Any, Dict, List
from abc import ABC, abstractmethod
from vertexai import generative_models

class LLMGeminiFamily(LLMBaseFamily):
    def __init__(self, model=LLMGeminiModels.GEMINI_1_5_PRO):
        super().__init__("Vertex AI Gemini")

        self._model = model.value

    def available_models(self) -> List[str]:
        return LLMGeminiModels.available_models()

    @property
    def model(self) -> LLMBaseModel:
        return self._model
