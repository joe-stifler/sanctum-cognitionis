class TestRedacaoModels(unittest.TestCase):
    def test_create_redacao(self):
        redacao = Redacao("Titulo", "2020-01-01", "Proposta 1", "Unicamp")
        self.assertEqual(redacao.titulo, "Titulo")

    def test_create_redacao_unicamp(self):
        redacao = RedacaoUnicamp("Titulo", "2020-01-01", "Proposta 1", "Unicamp")
        self.assertEqual(redacao.vestibular, "Unicamp")

if __name__ == '__main__':
    unittest.main()
