class LLMBaseFamily:
    def __init__(self, family_name: str):
        self._family_name = family_name

    def __str__(self) -> str:
        return self._family_name

    @property
    def family_name(self) -> str:
        return self._family_name
