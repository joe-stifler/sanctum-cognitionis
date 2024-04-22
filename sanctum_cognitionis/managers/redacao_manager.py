from sanctum_cognitionis.builders import RedacaoBuilder

class RedacaoManager:
    def __init__(self, dal, tabela_redacoes_propostas, tabela_redacoes_aluno, tabela_redacoes_candidatos, redacao_class):
        self.dal = dal
        self.redacao_class = redacao_class
        self.tabela_redacoes_aluno = tabela_redacoes_aluno
        self.tabela_redacoes_propostas = tabela_redacoes_propostas
        self.tabela_redacoes_candidatos = tabela_redacoes_candidatos

    def obter_redacao_aluno(self, query):
        data = self.dal.execute_query(self.tabela_redacoes_aluno, query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)

    def obter_redacao_candidato(self, query):
        data = self.dal.execute_query(self.tabela_redacoes_candidatos, query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)

    def obter_redacao_propostas(self, query):
        data = self.dal.execute_query(self.tabela_redacoes_propostas, query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)
