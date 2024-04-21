class TestLLMRedacao(unittest.TestCase):

    def setUp(self):
        self.llm_client = Mock()
        self.llm_client.generate = Mock(return_value="Feedback: excelente")
        self.redacao = LLMRedacao(self.llm_client)

    def test_corrigir_redacao(self):
        resultado = self.redacao.corrigir_redacao("Uma redação", "Proposta X", "Unicamp")
        expected = {
            'notas': {'G': 3},
            'comentários': {'geral': "Feedback: excelente"}
        }
        self.assertEqual(resultado, expected)
        self.llm_client.generate.assert_called()
