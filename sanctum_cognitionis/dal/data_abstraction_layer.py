class DataAbstractionLayer:
    def __init__(self, connectors):
        self.connectors = connectors

    def execute_query(self, query, source="csv"):
        connector = self.connectors.get(source)

        if not connector:
            raise ValueError("Conector não suportado.")

        return connector.execute_query(query)
