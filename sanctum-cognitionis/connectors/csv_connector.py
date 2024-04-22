import os
import pandas as pd
from unittest import TestCase, main

class CSVConnector:
    def __init__(self, file_path):
        self.file_path = file_path

    def connect(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError("O arquivo CSV não foi encontrado.")

    def execute_query(self, query):
        data = pd.read_csv(self.file_path)
        if 'filters' in query:
            for column, value in query['filters'].items():
                data = data[data[column] == value]
        if 'order_by' in query and 'ascending' in query:
            data = data.sort_values(by=query['order_by'], ascending=query['ascending'])
        return data

class TestCSVConnector(TestCase):
    def test_file_not_found(self):
        connector = CSVConnector("nonexistent.csv")
        with self.assertRaises(FileNotFoundError):
            connector.connect()

    def test_execute_query_with_filters_and_order(self):
        connector = CSVConnector("path/to/your/csvfile.csv")
        query = {
            'filters': {'column_name': 'value'},
            'order_by': 'some_column',
            'ascending': True
        }
        # Assuming the dataframe setup or mock setup here
        df = connector.execute_query(query)
        self.assertTrue(isinstance(df, pd.DataFrame))
