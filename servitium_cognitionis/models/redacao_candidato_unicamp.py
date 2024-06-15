from servitium_cognitionis.models.redacao_candidato import RedacaoCandidato

class RedacaoCandidatoUnicamp(RedacaoCandidato):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.nota_proposta_tematica_pt = kwargs["nota_proposta_tematica_pt"]
        self.comentarios_proposta_tematica_pt = kwargs["comentarios_proposta_tematica_pt"]
        self.nota_genero_g = kwargs["nota_genero_g"]
        self.comentarios_genero_g = kwargs["comentarios_genero_g"]
        self.nota_leitura_lt = kwargs["nota_leitura_lt"]
        self.comentarios_leitura_lt = kwargs["comentarios_leitura_lt"]
        self.nota_coesao_coerencia_cec = kwargs["nota_coesao_coerencia_cec"]

    def __str__(self):
        return f"RedacaoCandidatoUnicamp(nota_proposta_tematica_pt={self.nota_proposta_tematica_pt}, comentarios_proposta_tematica_pt={self.comentarios_proposta_tematica_pt}, nota_genero_g={self.nota_genero_g}, comentarios_genero_g={self.comentarios_genero_g}, nota_leitura_lt={self.nota_leitura_lt}, comentarios_leitura_lt={self.comentarios_leitura_lt}, nota_coesao_coerencia_cec={self.nota_coesao_coerencia_cec})"
