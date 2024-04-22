class LLMBaseFactory:
    """
    Factory for creating instances of LLMBase and its subclasses.
    """
    @staticmethod
    def create_base_llm(specialization: str = None, llm_client: Any) -> LLMBase:
        """
        Create an instance of LLMBase or a specialized subclass.

        Parameters:
            specialization (str, optional): The type of specialized LLMBase to create.
            llm_client (Any): An instance of an LLM client created by LLMFactoryClient.

        Returns:
            An instance of LLMBase or its subclass.
        """
        if specialization == "redacao":
            return RedacaoLLM(llm_client)
        else:
            return LLMBase(llm_client)
