import unittest
from connectors.csv_connector import CSVConnector
import pandas as pd

class TestCSVConnector(unittest.TestCase):
    def setUp(self):
        # Caminhos para os arquivos CSV para testes
        self.propostas_path = '/path/to/base-de-dados-propostas-redacoes-unicamp.csv'
        self.exemplos_path = '/path/to/base-de-dados-redacoes-exemplos-para-propostas-unicamp.csv'
        self.emilly_path = '/path/to/base-de-dados-redacoes-unicamp-feitas-por-emilly.csv'

    def test_read_propostas_csv(self):
        connector = CSVConnector(self.propostas_path)
        connector.connect()
        data = connector.execute_query({})
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)

    def test_read_exemplos_csv_with_filters(self):
        connector = CSVConnector(self.exemplos_path)
        connector.connect()
        query = {'filters': {'vestibular': '2020'}}
        data = connector.execute_query(query)
        self.assertEqual(data['vestibular'].unique(), ['2020'])

    def test_read_emilly_csv_with_order(self):
        connector = CSVConnector(self.emilly_path)
        connector.connect()
        query = {'order_by': 'nota', 'ascending': True}
        data = connector.execute_query(query)
        self.assertTrue(data['nota'].is_monotonic_increasing)

if __name__ == '__main__':
    unittest.main()
