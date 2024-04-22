# import unittest
# from unittest.mock import patch, Mock
# from your_module import LLMClientFactory, LLMBase, LLMBaseFactory, LLMRedacao

# class TestLLMClientFactory(unittest.TestCase):

#     @patch('your_module.OpenAI')
#     def test_create_openai_llm_with_defaults(self, mock_openai):
#         client = LLMClientFactory.create_llm('openai')
#         mock_openai.assert_called_once_with(api_key="default-openai-key")
#         self.assertIsInstance(client, mock_openai)

#     @patch('your_module.Gemini')
#     def test_create_gemini_llm_with_overrides(self, mock_gemini):
#         client = LLMClientFactory.create_llm('gemini', api_key="new-gemini-key")
#         mock_gemini.assert_called_once_with(api_key="new-gemini-key")
#         self.assertIsInstance(client, mock_gemini)

#     def test_create_unsupported_llm_raises_error(self):
#         with self.assertRaises(ValueError):
#             LLMClientFactory.create_llm('unsupported_llm')
