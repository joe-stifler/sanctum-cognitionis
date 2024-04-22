import streamlit as st
from servitium_cognitionis.connectors.csv_connector import CSVConnector
from servitium_cognitionis.data_access.data_interface import DataInterface
from servitium_cognitionis.models.redacao_candidato_unicamp import RedacaoCandidatoUnicamp
from servitium_cognitionis.managers.redacao_manager import RedacaoManager

# Configuração inicial para conectar com o banco de dados
def setup_data_access():
    table_mappings = {
        'redacoes_aluno': 'databases/redacao/unicamp/redacoes_aluno.csv',
        'redacoes_candidatos': 'databases/redacao/unicamp/redacoes_candidatos.csv',
        'redacoes_propostas': 'databases/redacao/unicamp/redacoes_propostas.csv'
    }
    csv_connector = CSVConnector(table_mappings)
    dal = DataInterface({'csv': csv_connector})
    return dal

# Instanciando o RedacaoManager
dal = setup_data_access()
redacao_manager = RedacaoManager(
    dal=dal,
    tabela_redacoes_propostas='redacoes_propostas',
    tabela_redacoes_aluno='redacoes_aluno',
    tabela_redacoes_candidatos='redacoes_candidatos',
    redacao_class=RedacaoCandidatoUnicamp
)

def main():
    st.title('Página de Redações')

    # Layout de três colunas
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.header("Vestibulares")
        vestibular = st.radio("Escolha o vestibular", ["Unicamp", "USP", "ENEM"])

        st.header("Redações")
        tipo_redacao = st.radio("Visualizar redações", ["Finalizadas", "Pendentes"])

        # Busca redações baseadas no tipo e no vestibular escolhido
        query = {"vestibular": vestibular.lower()}
        if tipo_redacao == "Finalizadas":
            redacoes = redacao_manager.obter_redacao_candidato(query)
        else:
            redacoes = redacao_manager.obter_redacao_propostas(query)

        for redacao in redacoes:
            st.write(f"{redacao.nome} - Nota: {redacao.nota_geral if hasattr(redacao, 'nota_geral') else 'N/A'}")

        # Galeria de Imagens (opcional)
        st.image("path_to_image.jpg", caption="Imagem Redação")

    with col2:
        st.header("Coletânea de Textos")
        # Exibição da coletânea selecionada
        coletanea_selecionada = st.selectbox("Escolha a proposta de redação", [r.nome for r in redacoes])
        texto_coletanea = next((r.texto_proposta for r in redacoes if r.nome == coletanea_selecionada), "")
        st.text_area("Texto Coletânea", texto_coletanea, height=300)

        st.header("Escreva sua redação")
        texto_redacao = st.text_area("Redação", "Digite sua redação aqui", height=300)
        if st.button("Enviar para Correção"):
            st.write("Redação enviada para correção!")

    with col3:
        st.header("Feedback do Tutor")
        if st.button("Obter Feedback"):
            # Simulação de feedback
            st.write("Bom uso de argumentos, mas precisa melhorar a coesão.")

        st.header("Notas por Critério")
        notas = {
            "Proposta Temática (Pt)": 2,
            "Gênero (G)": 3,
            "Leitura (Lt)": 3,
            "Convenções da Escrita e Coesão (CeC)": 4
        }
        st.json(notas)

        if st.button("Atualizar Notion"):
            st.write("Notas atualizadas no Notion!")

if __name__ == "__main__":
    main()
