from servitium_cognitionis.llms import LLMFamily

from typing import Type, Any, Dict
from vertexai import generative_models

class LLMClientFactory:
    """
    Factory for creating Language Learning Models (LLMs).
    Supports various LLMs like OpenAI, Gemini, Llama, and MistralAI.
    Users need to provide only the LLM type (as an LLMFamily ENUM) and optional specific kwargs.
    """

    @staticmethod
    def get_all_models(llm_family: LLMFamily) -> Any:
        """
        Get all available models for a given LLM type.
        
        Parameters:
            llm_family (LLMFamily): Type of LLM to get models for.

        Returns:
            A list of available models for the specified LLM.

        Raises:
            ValueError: If the llm_family is not supported.
        """
        return llm_family.config['available_models']
    
    @staticmethod
    def create_llm(llm_family: LLMFamily, llm_model: str) -> Any:
        """
        Create an LLM instance with sensible defaults and optional overrides.

        Parameters:
            llm_family (LLMFamily): Type of LLM to create, ENUM of supported families.
            llm_model (str): Model to use for the LLM.

        Returns:
            An instance of the specified LLM.

        Raises:
            ValueError: If the llm_family is not supported.
        """
        if llm_family in LLMFamily:
            llm_config = llm_family.config
            # Assuming the creation logic here based on the configuration
            # You might need to integrate with the actual API calls or other logic.
            return "LLM instance created with model: " + llm_model
        else:
            raise ValueError(f"Unsupported LLM type: {llm_family}")
