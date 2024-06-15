from servitium_cognitionis.llms.base import LLMBaseFamily
from servitium_cognitionis.llms.mock import (
    LLMMockBaseModel, LLMMockModel
)

from typing import List

class LLMMockFamily(LLMBaseFamily):
    def __init__(self):
        super().__init__("Mock AI Family")

    def model_names(self) -> List[str]:
        return [str(LLMMockModel()), ]

    def get_model(self, model_name: str) -> LLMMockBaseModel:
        return LLMMockModel()
