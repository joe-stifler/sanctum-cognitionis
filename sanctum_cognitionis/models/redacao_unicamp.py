from sanctum_cognitionis.models.redacao import Redacao

class RedacaoUnicamp(Redacao):
    def __init__(self, nota_proposta_tematica_pt, comentarios_proposta_tematica_pt, nota_genero_g, comentarios_genero_g, nota_leitura_lt, comentarios_leitura_lt, nota_coesao_coerencia_cec, comentarios_coesao_coerencia_cec, *args):
        super().__init__(*args)

        self.nota_proposta_tematica_pt = nota_proposta_tematica_pt
        self.comentarios_proposta_tematica_pt = comentarios_proposta_tematica_pt
        self.nota_genero_g = nota_genero_g
        self.comentarios_genero_g = comentarios_genero_g
        self.nota_leitura_lt = nota_leitura_lt
        self.comentarios_leitura_lt = comentarios_leitura_lt
        self.nota_coesao_coerencia_cec = nota_coesao_coerencia_cec
        self.comentarios_coesao_coerencia_cec = comentarios_coesao_coerencia_cec
