import unittest
from sanctum_cognitionis.models.redacao_proposta import RedacaoProposta
from sanctum_cognitionis.connectors.csv_connector import CSVConnector
from sanctum_cognitionis.models.redacao_candidato_unicamp import RedacaoCandidatoUnicamp
from sanctum_cognitionis.managers.redacao_manager import RedacaoManager
from sanctum_cognitionis.dal.data_abstraction_layer import DataAbstractionLayer

class TestRedacaoManager(unittest.TestCase):
    def setUp(self):
        table_mappings = {
            'redacoes_aluno': 'databases/redacao/unicamp/redacoes_aluno.csv',
            'redacoes_candidatos': 'databases/redacao/unicamp/redacoes_candidatos.csv',
            'redacoes_propostas': 'databases/redacao/unicamp/redacoes_propostas.csv'
        }
        csv_connector = CSVConnector(table_mappings)
        dal = DataAbstractionLayer({'csv': csv_connector})
        
        self.manager = RedacaoManager(
            dal=dal,
            tabela_redacoes_propostas='redacoes_propostas',
            tabela_redacoes_aluno='redacoes_aluno',
            tabela_redacoes_candidatos='redacoes_candidatos',
            redacao_class=RedacaoCandidatoUnicamp
        )

    def test_obter_redacao_aluno(self):
        resultado = self.manager.obter_redacao_aluno()
        self.assertIsInstance(resultado, list)
        self.assertIsInstance(resultado[0], RedacaoCandidatoUnicamp)

    def test_obter_redacao_candidato(self):
        resultado = self.manager.obter_redacao_candidato()
        self.assertIsInstance(resultado, list)
        self.assertIsInstance(resultado[0], RedacaoCandidatoUnicamp)

    def test_obter_propostas_redacao(self):
        resultado = self.manager.obter_redacao_propostas()
        self.assertIsInstance(resultado, list)
        self.assertIsInstance(resultado[0], RedacaoProposta)

if __name__ == '__main__':
    unittest.main()
