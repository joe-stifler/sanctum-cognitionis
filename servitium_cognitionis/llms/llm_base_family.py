from typing import Any, Dict
from abc import ABC, abstractmethod
from vertexai import generative_models

class LLMBaseFamily(ABC):
    def __init__(self, family_name: str):
        self._family_name = family_name

    def __str__(self) -> str:
        return self._family_name

    @property
    def family_name(self) -> str:
        return self._family_name

    @abstractmethod
    def available_models(self):
        pass

    @abstractmethod
    def create_model(self) -> Any:
        pass
