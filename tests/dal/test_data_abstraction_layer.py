import unittest
import pandas as pd
from sanctum_cognitionis.connectors.csv_connector import CSVConnector
from sanctum_cognitionis.dal.data_abstraction_layer import DataAbstractionLayer

class TestDataAbstractionLayer(unittest.TestCase):
    def setUp(self):
        self.csv_connector = CSVConnector('databases/redacao/unicamp/redacoes_aluno.csv')
        self.dal = DataAbstractionLayer({'csv': self.csv_connector})

    def test_data_retrieval_type(self):
        query = {
            'filters': {'ano_vestibular': 2023},
            'order_by': [
                'numero_proposta'
            ],
            'ascending': [True, ]
        }
        data = self.dal.execute_query(query)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertEqual(data['ano_vestibular'].iloc[0], 2023)

if __name__ == '__main__':
    unittest.main()
