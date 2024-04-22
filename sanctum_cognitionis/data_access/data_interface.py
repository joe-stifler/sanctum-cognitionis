class DataInterface:
    def __init__(self, connectors):
        self.connectors = connectors

    def execute_query(self, table_name, query, source="csv"):
        connector = self.connectors.get(source)

        if not connector:
            raise ValueError("Conector não suportado.")

        return connector.execute_query(table_name, query)
