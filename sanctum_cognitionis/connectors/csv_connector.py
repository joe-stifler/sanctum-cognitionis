import json
import pandas as pd

class CSVConnector:
    def __init__(self, file_path):
        self.file_path = file_path

    def _extract_database_name(self, file_path):
        return file_path.split('/')[-1].split('.')[0]

    def connect(self):
        if not pd.io.common.is_url(self.file_path) and not pd.io.common.file_exists(self.file_path):
            raise FileNotFoundError("O arquivo CSV não foi encontrado.")

    def execute_query(self, query):
        data = pd.read_csv(self.file_path)
        if 'filters' in query:
            for column, value in query['filters'].items():
                data = data[data[column] == value]

        if 'order_by' in query and 'ascending' in query:
            data = data.sort_values(by=query['order_by'], ascending=query['ascending'])

        return data
