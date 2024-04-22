import unittest
import pandas as pd
from sanctum_cognitionis.connectors.csv_connector import CSVConnector

class TestCSVConnector(unittest.TestCase):
    def setUp(self):
        self.base_folder = "databases/redacao/unicamp"
        self.schema_path = self.base_folder + "/schema.json"

    def test_execute_query_with_filters_and_order(self):
        database_path = self.base_folder + "/redacoes_propostas.csv"
        connector = CSVConnector(database_path)
        connector.connect()
        query = {
            'filters': {'ano_vestibular': 2020},
            'order_by': [
                'numero_proposta'
            ],
            'ascending': [True, ]
        }
        data = connector.execute_query(query)
        self.assertTrue(isinstance(data, pd.DataFrame))
        self.assertEqual(data['ano_vestibular'].iloc[0], 2020)

if __name__ == '__main__':
    unittest.main()
