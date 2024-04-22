from builders import RedacaoBuilder

class RedacaoManager:
    def __init__(self, dal, tabela_redacoes_propostas, tabela_redacoes_aluno, tabela_redacoes_candidatos, redacao_class):
        self.dal = dal
        self.redacao_class = redacao_class
        self.tabela_redacoes_aluno = tabela_redacoes_aluno
        self.tabela_redacoes_propostas = tabela_redacoes_propostas
        self.tabela_redacoes_candidatos = tabela_redacoes_candidatos

    def obter_redacao_aluno(self, query):
        data = self.dal.get_data(query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)

    def obter_redacao_candidato(self, query):
        data = self.dal.get_data(query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)

    def obter_propostas_redacao(self, query):
        data = self.dal.get_data(query, source='csv')
        return RedacaoBuilder.build_list(data, self.redacao_class)
