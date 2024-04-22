class RedacaoBuilder:
    @staticmethod
    def build_list(data, redacao_class):
        redacoes = []
        for index, row in data.iterrows():
            # Validação de dados para garantir que campos essenciais estão presentes e são válidos
            required_fields = ['nome', 'redacao_candidato', 'numero_proposta', 'ano_vestibular']
            if any(row[field] is None for field in required_fields):
                raise ValueError(f"Dados inválidos na linha {index+1}: Campos requeridos estão faltando ou nulos.")

            # Tratamento de tipos para garantir que os dados estão no formato correto
            try:
                row['ano_vestibular'] = int(row['ano_vestibular'])
                row['nota_geral'] = float(row['nota_geral']) if row['nota_geral'] else None
            except ValueError as e:
                raise ValueError(f"Erro de tipo na linha {index+1}: {e}")

            # Criação do objeto RedacaoUnicamp utilizando desempacotamento de dicionário
            redacoes.append(redacao_class(**row.to_dict()))
        return redacoes
