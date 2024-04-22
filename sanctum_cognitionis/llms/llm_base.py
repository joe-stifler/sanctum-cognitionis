class LLMBase:
    def __init__(self, llm_client):
        self.llm = llm_client

    def gerar_texto(self, prompt, contexto=None):
        if contexto:
            prompt = f"{contexto}\n\n{prompt}"
        response = self.llm.generate(prompt)
        return response
