from managers.redacao_manager import RedacaoManager

class TestRedacaoManager(unittest.TestCase):
    def setUp(self):
        self.manager = RedacaoManager(DataAbstractionLayer({'csv': CSVConnector('/path/to/csv')}), 'redacoes')

    def test_obter_redacoes(self):
        redacoes = self.manager.obter_redacoes()
        self.assertIsInstance(redacoes, list)

if __name__ == '__main__':
    unittest.main()
