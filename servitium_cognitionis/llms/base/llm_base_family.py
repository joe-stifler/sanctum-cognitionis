from servitium_cognitionis.llms.base import LLMBaseModel

from typing import List
from abc import ABC, abstractmethod

class LLMBaseFamily(ABC):
    def __init__(self, family_name: str):
        self._family_name = family_name

    def __str__(self) -> str:
        return self._family_name

    @property
    def family_name(self) -> str:
        return self._family_name

    @abstractmethod
    def model_names(self) -> List[str]:
        pass

    @abstractmethod
    def get_model(self, model_name: str) -> LLMBaseModel:
        pass
