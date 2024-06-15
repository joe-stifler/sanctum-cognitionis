from servitium_cognitionis.llms.base import LLMBaseFamily
from servitium_cognitionis.llms.gemini import (
    GeminiDevBaseModel,
    GeminiDevModelPro1_5,
    GeminiDevModel1_5_Flash,
)

from typing import List


class GeminiDevFamily(LLMBaseFamily):
    def __init__(self):
        super().__init__("Gemini Dev AI Family")

        available_models = [
            GeminiDevModelPro1_5(),
            GeminiDevModel1_5_Flash(),
        ]

        self._available_models = {
            available_model.__class__.__name__: available_model
            for available_model in available_models
        }

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def model_names(self) -> List[str]:
        return self._available_models.keys()

    def get_model(self, model_name: str) -> GeminiDevBaseModel:
        if model_name not in self.model_names():
            raise ValueError(
                f"Model {model_name} not found in {self.name} family. Available models: {self.model_names()}"
            )

        return self._available_models[model_name]
