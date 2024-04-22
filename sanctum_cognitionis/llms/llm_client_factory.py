from langchain.llms import OpenAI, Gemini, Llama
from langchain.llms.mistral import MistralAI
from typing import Type, Any, Dict

class LLMClientFactory:
    """
    Factory for creating Language Learning Models (LLMs).
    Supports various LLMs like OpenAI, Gemini, Llama, and MistralAI.
    Users need to provide only the LLM type and optional specific kwargs.
    """
    llm_defaults: Dict[str, Dict[str, Any]] = {
        "openai": {"api_key": "default-openai-key"},
        "gemini": {"api_key": "default-gemini-key"},
        "llama": {"model_path": "path/to/llama"},
        "mistral": {"model_name": "base-model", "api_key": "default-mistral-key"}
    }
    llm_types: Dict[str, Type[Any]] = {
        "openai": OpenAI,
        "gemini": Gemini,
        "llama": Llama,
        "mistral": MistralAI
    }

    @staticmethod
    def create_llm(llm_type: str, **kwargs) -> Any:
        """
        Create an LLM instance with sensible defaults and optional overrides.

        Parameters:
            llm_type (str): Type of LLM to create, keys must be in llm_defaults.
            **kwargs: Optional keyword arguments to override defaults.

        Returns:
            An instance of the specified LLM.

        Raises:
            ValueError: If the llm_type is not supported.
        """
        if llm_type in LLMFactoryClient.llm_defaults:
            params = {**LLMFactoryClient.llm_defaults[llm_type], **kwargs}
            llm_class = LLMFactoryClient.llm_types[llm_type]
            return llm_class(**params)
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
