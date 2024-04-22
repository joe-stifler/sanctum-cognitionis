class Deltalake:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Deltalake, cls).__new__(cls)
        return cls.instance

    def read_data(self, query):
        # Aqui seria implementado a lógica para ler dados
        pass
