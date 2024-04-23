from servitium_cognitionis.llms import LLMBaseFamily, LLMGeminiModels, LLMBaseModel

from typing import List
from vertexai import generative_models

class LLMGeminiFamily(LLMBaseFamily):
    def __init__(self):
        super().__init__("Vertex AI Gemini")

        self._available_models = {
            str(available_model.value): available_model.value for available_model in LLMGeminiModels
        }
        self._current_model_name = str(list(self.available_model_names())[0])

    def get_available_model(self, model_name: str) -> LLMBaseModel:
        return self._available_models[model_name]

    def available_model_names(self) -> List[str]:
        return self._available_models.keys()

    def update_available_model(self, model):
        self._available_models[str(model)] = model
        
    def current_model(self) -> LLMBaseModel:
        return self._available_models[self.current_model_name()]

    def current_model_name(self) -> str:
        return self._current_model_name
    
    def current_model_index(self) -> int:
        available_models = self.available_model_names()
        for i, model in enumerate(available_models):
            if model == self.current_model_name():
                return i
        raise ValueError("Invalid model name")

    def update_current_model_name(self, model_name):
        self._current_model_name = model_name
