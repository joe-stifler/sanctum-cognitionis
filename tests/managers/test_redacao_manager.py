import unittest
import pandas as pd
from sanctum_cognitionis.connectors.csv_connector import CSVConnector
from sanctum_cognitionis.models.redacao_unicamp import RedacaoUnicamp
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
            redacao_class=RedacaoUnicamp
        )

    def test_obter_redacao_aluno(self):
        query = {}
        resultado = self.manager.obter_redacao_aluno(query)
        self.assertIsInstance(resultado, list)
        self.assertIsInstance(resultado[0], RedacaoUnicamp)

    # def test_obter_redacao_candidato(self):
    #     query = {'filters': {'nome': 'Maria'}}
    #     self.manager.obter_redacao_candidato(query)
    #     self.dal_mock.get_data.assert_called_once_with(query, source='csv')

    # def test_obter_propostas_redacao(self):
    #     query = {}
    #     self.manager.obter_propostas_redacao(query)
    #     self.dal_mock.get_data.assert_called_once_with(query, source='csv')

if __name__ == '__main__':
    unittest.main()
