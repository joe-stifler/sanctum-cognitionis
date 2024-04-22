import pandas as pd

class CSVConnector:
    def __init__(self, table_mappings):
        self.table_mappings = table_mappings

    def connect(self):
        for table_name, file_path in self.table_mappings.items():
            if not pd.io.common.is_url(file_path) and not pd.io.common.file_exists(file_path):
                raise FileNotFoundError(f"O arquivo CSV '{file_path}' para a tabela '{table_name}' não foi encontrado.")

    def execute_query(self, table_name, query):
        file_path = self.table_mappings.get(table_name)
        if not file_path:
            raise ValueError(f"Tabela '{table_name}' não encontrada no mapeamento.")

        data = pd.read_csv(file_path)

        if 'filters' in query:
            for column, value in query['filters'].items():
                data = data[data[column] == value]

        if 'order_by' in query and 'ascending' in query:
            data = data.sort_values(by=query['order_by'], ascending=query['ascending'])

        return data
