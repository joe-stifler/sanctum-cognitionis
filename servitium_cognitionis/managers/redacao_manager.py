from servitium_cognitionis.models import RedacaoPropostaUnicamp
from servitium_cognitionis.models import RedacaoCandidatoUnicamp

class RedacaoManager:
    def __init__(self, dal, tabela_redacoes_propostas, tabela_redacoes_aluno, tabela_redacoes_candidatos):
        self.data_access = dal
        self.tabela_redacoes_aluno = tabela_redacoes_aluno
        self.tabela_redacoes_propostas = tabela_redacoes_propostas
        self.tabela_redacoes_candidatos = tabela_redacoes_candidatos

    def _build_redacao_object_list(self, data, redacao_class):
        return [redacao_class(**row.to_dict()) for _, row in data.iterrows()]

    def obter_redacao_aluno(self, _vestibular, query={}):
        data = self.data_access.execute_query(self.tabela_redacoes_aluno, query, source='csv')
        return self._build_redacao_object_list(data, RedacaoCandidatoUnicamp)

    def obter_redacao_candidato(self, _vestibular, query={}):
        data = self.data_access.execute_query(self.tabela_redacoes_candidatos, query, source='csv')
        return self._build_redacao_object_list(data, RedacaoCandidatoUnicamp)

    def obter_redacao_propostas(self, _vestibular, query={}):
        data = self.data_access.execute_query(self.tabela_redacoes_propostas, query, source='csv')
        return self._build_redacao_object_list(data, RedacaoPropostaUnicamp)
