# import unittest
# import pandas as pd
# from servitium_cognitionis.connectors.csv_connector import CSVConnector
# from servitium_cognitionis.data_access.data_interface import DataInterface

# class TestDataInterface(unittest.TestCase):
#     def setUp(self):
#         table_mappings = {
#             'redacoes_aluno': 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv',
#             'redacoes_candidatos': 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
#             'redacoes_propostas': 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv'
#         }
#         self.csv_connector = CSVConnector(table_mappings)
#         self.data_access = DataInterface({'csv': self.csv_connector})

#     def test_data_retrieval_type(self):
#         query = {
#             'filters': {'ano_vestibular': 2023},
#             'order_by': [
#                 'numero_proposta'
#             ],
#             'ascending': [True, ]
#         }
#         data = self.data_access.execute_query('redacoes_aluno', query)
#         self.assertTrue(isinstance(data, pd.DataFrame))
#         self.assertEqual(data['ano_vestibular'].iloc[0], 2023)

# if __name__ == '__main__':
#     unittest.main()
