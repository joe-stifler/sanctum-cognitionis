class RedacaoManager:
    def __init__(self, dal, table_name):
        self.dal = dal
        self.table_name = table_name

    def obter_redacoes(self, vestibular=None):
        query = {'filters': {'vestibular': vestibular}} if vestibular else {}
        return self.dal.get_data(query, source='csv')
