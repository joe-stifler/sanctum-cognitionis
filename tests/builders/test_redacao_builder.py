import unittest
import pandas as pd
from sanctum_cognitionis.models.redacao_unicamp import RedacaoUnicamp
from sanctum_cognitionis.builders.redacao_builder import RedacaoBuilder

class TestRedacaoBuilder(unittest.TestCase):
    def test_build_list_valid_data(self):
        data = pd.DataFrame({
            'nome': ['João'],
            'qualidade': ['Mediana'],
            'redacao_candidato': ['Exemplo de redação'],
            'numero_proposta': [1],
            'ano_vestibular': ['2020'],
            'nota_geral': ['9.5'],
            'comentario_geral':  ['Exemplo de comentário geral.'],
            'comentarios_corretor': ['Muito bem elaborada.'],
            'nota_proposta_tematica_pt': [2],
            'comentarios_proposta_tematica_pt': ['Exemplo de comentário.'],
            'nota_genero_g': [3.0],
            'comentarios_genero_g': ['Exemplo de comentário.'],
            'nota_leitura_lt': [2.5],
            'comentarios_leitura_lt': ['Exemplo de comentário.'],
            'nota_coesao_coerencia_cec': [1],
            'comentarios_coesao_coerencia_cec': ['Ótimo trabalho']
        })
        redacoes = RedacaoBuilder.build_list(data, RedacaoUnicamp)
        self.assertIsInstance(redacoes, list)
        self.assertIsInstance(redacoes[0], RedacaoUnicamp)
        self.assertEqual(redacoes[0].nome, 'João')

    def test_build_list_invalid_column_name(self):
        data = pd.DataFrame({
            'nome': ['João'],
            'qualidade': ['Mediana'],
            'redacao_candidatos': ['Exemplo de redação'],
            'numero_proposta': [1],
            'ano_vestibular': ['2020'],
            'nota_geral': ['9.5'],
            'comentario_geral':  ['Exemplo de comentário geral.'],
            'comentarios_corretor': ['Muito bem elaborada.'],
            'nota_proposta_tematica_pt': [2],
            'comentarios_proposta_tematica_pt': ['Exemplo de comentário.'],
            'nota_genero_g': [3.0],
            'comentarios_genero_g': ['Exemplo de comentário.'],
            'nota_leitura_lt': [2.5],
            'comentarios_leitura_lt': ['Exemplo de comentário.'],
            'nota_coesao_coerencia_cec': [1],
            'comentarios_coesao_coerencia_cec': ['Ótimo trabalho']
        })
        with self.assertRaises(KeyError):
            RedacaoBuilder.build_list(data, RedacaoUnicamp)

if __name__ == '__main__':
    unittest.main()
