import unittest
from unittest.mock import MagicMock
from managers.redacao_manager import RedacaoManager
from models.redacao import Redacao, RedacaoUnicamp

class TestRedacaoManager(unittest.TestCase):
    def setUp(self):
        self.dal_mock = MagicMock()
        self.manager = RedacaoManager(
            dal=self.dal_mock,
            tabela_redacoes_propostas='redacoes_propostas.csv',
            tabela_redacoes_aluno='redacoes_aluno.csv',
            tabela_redacoes_candidatos='redacoes_candidatos.csv',
            redacao_class=RedacaoUnicamp
        )

    def test_obter_redacao_aluno(self):
        query = {'filters': {'nome': 'João'}}
        self.dal_mock.get_data.return_value = pd.DataFrame({
            'nome': ['João'],
            'redacao_candidato': ['Texto da redação'],
            'numero_proposta': [1],
            'ano_vestibular': [2020],
            'nota_geral': [10],
            'comentarios_corretor': ['Excelente trabalho.']
        })
        resultado = self.manager.obter_redacao_aluno(query)
        self.dal_mock.get_data.assert_called_once_with(query, source='csv')
        self.assertIsInstance(resultado, list)
        self.assertIsInstance(resultado[0], RedacaoUnicamp)

    def test_obter_redacao_candidato(self):
        query = {'filters': {'nome': 'Maria'}}
        self.manager.obter_redacao_candidato(query)
        self.dal_mock.get_data.assert_called_once_with(query, source='csv')

    def test_obter_propostas_redacao(self):
        query = {}
        self.manager.obter_propostas_redacao(query)
        self.dal_mock.get_data.assert_called_once_with(query, source='csv')

if __name__ == '__main__':
    unittest.main()
