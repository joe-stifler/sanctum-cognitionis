# class TestLLMBase(unittest.TestCase):

#     def setUp(self):
#         self.llm_client = Mock()
#         self.llm_client.generate = Mock(return_value="Generated text")
#         self.base = LLMBase(self.llm_client)

#     def test_gerar_texto_without_context(self):
#         response = self.base.gerar_texto("Test prompt")
#         self.llm_client.generate.assert_called_once_with("Test prompt")
#         self.assertEqual(response, "Generated text")

#     def test_gerar_texto_with_context(self):
#         response = self.base.gerar_texto("Test prompt", "Context here")
#         self.llm_client.generate.assert_called_once_with("Context here\n\nTest prompt")
#         self.assertEqual(response, "Generated text")
