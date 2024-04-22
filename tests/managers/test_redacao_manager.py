import unittest
import pandas as pd
from sanctum_cognitionis.dal import DataAbstractionLayer
from sanctum_cognitionis.models.redacao_unicamp import RedacaoUnicamp
from sanctum_cognitionis.managers.redacao_manager import RedacaoManager

class TestRedacaoManager(unittest.TestCase):
    def setUp(self):
        
        
        self.manager = RedacaoManager(
            dal=self.dal_mock,
            tabela_redacoes_propostas='redacoes_propostas',
            tabela_redacoes_aluno='redacoes_aluno',
            tabela_redacoes_candidatos='redacoes_candidatos',
            redacao_class=RedacaoUnicamp
        )

    def test_obter_redacao_aluno(self):
        query = {}
    #     self.dal_mock.get_data.return_value = pd.DataFrame({
    #         'nome': ['João'],
    #         'redacao_candidato': ['Texto da redação'],
    #         'numero_proposta': [1],
    #         'ano_vestibular': [2020],
    #         'nota_geral': [10],
    #         'comentarios_corretor': ['Excelente trabalho.']
    #     })
        resultado = self.manager.obter_redacao_aluno(query)
        print(resultado)
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
