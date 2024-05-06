from servitium_cognitionis.llms.base import LLMBaseFamily
from servitium_cognitionis.llms.gemini import (
    GeminiVertexAIBaseModel, GeminiVertexAIModel1_5Pro, GeminiVertexAIModel1_0Pro002, GeminiVertexAIModelExperimental
)

from typing import List

class GeminiVertexAIFamily(LLMBaseFamily):
    def __init__(self):
        super().__init__("Gemini Vertex AI Family")

        available_models = [
            GeminiVertexAIModelExperimental(),
            GeminiVertexAIModel1_5Pro(),
            GeminiVertexAIModel1_0Pro002(),
        ]

        self._available_models = {
            str(available_model): available_model for available_model in available_models
        }

    def model_names(self) -> List[str]:
        return self._available_models.keys()

    def get_model(self, model_name: str) -> GeminiVertexAIBaseModel:
        if model_name not in self._available_models:
            raise ValueError(f"Model {model_name} not found in {self.name} family.")

        return self._available_models[model_name]
