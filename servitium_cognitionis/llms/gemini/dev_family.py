from servitium_cognitionis.llms.base import LLMBaseFamily
from servitium_cognitionis.llms.gemini import GeminiDevBaseModel, GeminiDevModelPro

from typing import List

class GeminiDevFamily(LLMBaseFamily):
    def __init__(self):
        super().__init__("Gemini Dev AI Family")

        available_models = [
            GeminiDevModelPro(),
        ]

        self._available_models = {
            str(available_model): available_model for available_model in available_models
        }

    def model_names(self) -> List[str]:
        return self._available_models.keys()

    def get_model(self, model_name: str) -> GeminiDevBaseModel:
        if model_name not in self._available_models:
            raise ValueError(f"Model {model_name} not found in {self.name} family.")

        return self._available_models[model_name]
