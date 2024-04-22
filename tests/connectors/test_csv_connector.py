import unittest
import pandas as pd
from servitium_cognitionis.connectors.csv_connector import CSVConnector

class TestCSVConnector(unittest.TestCase):
    def setUp(self):
        self.base_folder = "databases/redacao/unicamp"
        self.table_mappings = {
            'redacoes_propostas': self.base_folder + "/redacoes_propostas.csv",
            'redacoes_candidatos': self.base_folder + "/redacoes_candidatos.csv",
            'redacoes_aluno': self.base_folder + "/redacoes_aluno.csv",
        }
        self.connector = CSVConnector(self.table_mappings)
        self.connector.connect()

    def test_execute_query_with_filters_and_order(self):
        query = {
            'filters': {'ano_vestibular': 2020},
            'order_by': ['numero_proposta'],
            'ascending': [True],
        }
        data = self.connector.execute_query('redacoes_propostas', query)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertEqual(data['ano_vestibular'].iloc[0], 2020)
    
    def test_execute_query_without_filters_and_order(self):
        data = self.connector.execute_query('redacoes_candidatos')
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertTrue(2020 in data['ano_vestibular'].values)


if __name__ == '__main__':
    unittest.main()
