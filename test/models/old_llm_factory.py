import unittest
from sanctum_cognitionis import LLMFactory  # Import your LLMFactory from its module

class TestLLMFactory(unittest.TestCase):

    def test_create_openai_with_defaults(self):
        llm = LLMFactory.create_llm("openai")
        self.assertIsInstance(llm, OpenAI)

    def test_create_gemini_with_overrides(self):
        llm = LLMFactory.create_llm("gemini", api_key="new-api-key")
        self.assertIsInstance(llm, Gemini)
        self.assertEqual(llm.api_key, "new-api-key")

    def test_create_llama_with_defaults(self):
        llm = LLMFactory.create_llm("llama")
        self.assertIsInstance(llm, Llama)

    def test_create_mistral_with_overrides(self):
        llm = LLMFactory.create_llm("mistral", model_name="advanced-model")
        self.assertIsInstance(llm, MistralAI)
        self.assertEqual(llm.model_name, "advanced-model")

    def test_create_unsupported_llm(self):
        with self.assertRaises(ValueError):
            LLMFactory.create_llm("unsupported")

if __name__ == "__main__":
    unittest.main()
