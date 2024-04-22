import unittest
import pandas as pd
from sanctum_cognitionis.models.redacao_unicamp import RedacaoUnicamp
from sanctum_cognitionis.builders.redacao_builder import RedacaoBuilder

class TestRedacaoBuilder(unittest.TestCase):
    def test_build_list_valid_data(self):
        data = pd.DataFrame({
            'nome': ['João'],
            'redacao_candidato': ['Exemplo de redação'],
            'numero_proposta': [1],
            'ano_vestibular': ['2020'],
            'nota_geral': ['9.5'],
            'comentarios_corretor': ['Muito bem elaborada.']
        })
        redacoes = RedacaoBuilder.build_list(data, RedacaoUnicamp)
        self.assertIsInstance(redacoes, list)
        self.assertIsInstance(redacoes[0], RedacaoUnicamp)
        self.assertEqual(redacoes[0].nome, 'João')

    def test_build_list_invalid_data(self):
        data = pd.DataFrame({
            'nome': [None],
            'redacao_candidato': ['Exemplo de redação sem nome'],
            'numero_proposta': [1],
            'ano_vestibular': ['2020'],
            'nota_geral': ['9.5'],
            'comentarios_corretor': ['Muito bem elaborada.']
        })
        with self.assertRaises(ValueError):
            RedacaoBuilder.build_list(data, RedacaoUnicamp)

if __name__ == '__main__':
    unittest.main()
