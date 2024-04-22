import time
import pandas as pd
import streamlit as st

from header import show_header
show_header(0)

import plotly.graph_objects as go
from chat_interface import ChatInterface

from servitium_cognitionis.connectors.csv_connector import CSVConnector
from servitium_cognitionis.data_access.data_interface import DataInterface
from servitium_cognitionis.models.redacao_candidato_unicamp import RedacaoCandidatoUnicamp
from servitium_cognitionis.managers.redacao_manager import RedacaoManager

def setup_data_access():
    table_mappings = {
        'redacoes_aluno': 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv',
        'redacoes_candidatos': 'databases/redacao/unicamp/unicamp_unicamp_redacoes_candidatos.csv',
        'redacoes_propostas': 'databases/redacao/unicamp/unicamp_unicamp_redacoes_propostas.csv'
    }
    csv_connector = CSVConnector(table_mappings)
    dal = DataInterface({'csv': csv_connector})
    return dal

def generate_scorings(scores):
    max_score = 4
    criteria = ["Proposta Temática (Pt)", "Gênero (G)", "Leitura (Lt)", "Convenções da Escrita e Coesão (CeC)"]
    icons = ["🎯", "📚", "🔍", "✍️"]

    for crit, icon, score in zip(criteria, icons, scores):
        st.progress(score / max_score)
        st.caption(f'{icon} {crit}: {score}/{max_score}')

    st.divider()
    score_sum = sum(scores)
    max_score_overall = 12
    
    # generate an icon to represent an overall score
    icon = "📝"
    
    st.progress(score_sum / max_score_overall)
    st.caption(f'📝 Somatório Total: {score_sum}/{max_score_overall}')

def display_files_with_checkboxes_and_downloads(file_info):
    """
    Display checkboxes and download buttons for files.

    :param file_info: A list of tuples containing the filename for the label and the file path for downloading
    """
    for file_label, file_path in file_info:
        # Create two columns: one for the checkbox, one for the download button
        col1, col2 = st.columns([1, 2])

        # In the first column, display the checkbox
        with col1:
            checkbox_label = f"Enable download for {file_label}"
            is_checked = st.checkbox(checkbox_label, value=True, key=f"checkbox_{file_label}")

        # In the second column, display the download button
        with col2:
            download_label = f"Download {file_label}"
            with open(file_path, "rb") as file:
                download_button = st.download_button(
                    label=download_label,
                    data=file,
                    file_name=file_label,
                    disabled=not is_checked,  # Button is enabled/disabled based on the checkbox
                    mime='text/csv',  # or 'application/octet-stream', etc.
                    key=f"download_{file_label}"
                )

# Example usage
file_info = [
    ("redacoes_aluno.csv", 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv'),
    ("unicamp_redacoes_candidatos.csv", 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv'),
    ("unicamp_redacoes_propostas.csv", 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv'),
    ("grade_de_correcao_analitica_unicamp.txt", 'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt')
]

def main():
    dal = setup_data_access()
    redacao_manager = RedacaoManager(
        dal=dal,
        tabela_redacoes_propostas='redacoes_propostas',
        tabela_redacoes_aluno='redacoes_aluno',
        tabela_redacoes_candidatos='redacoes_candidatos',
        redacao_class=RedacaoCandidatoUnicamp
    )

    # write `Página de Redações` in the center of screen
    # centralize the text using markdown
    st.markdown("<h1 style='text-align: center;'>📚 Página de Redações 📚</h1>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        session_id = "redacoes"
        user_name = "estudante"
        user_avatar = "👩🏾‍🎓"
        ai_name = "professor"
        ai_avatar = "👩🏽‍🏫"
        ai_first_message = "Olá! Meu nome é Dani Stella, como posso te ajudar?"
        
        # expander_persona = st.expander("Persona do professor(a)", expanded=True)
        with st.expander("Nome da Persona do Professor(a)", expanded=False):
            persona_name = st.text_input(
                "Nome da persona do professor(a)",
                "Dani Stella: Mentora de Redação Unicamp",
                label_visibility='collapsed'
            )
        with st.expander("Breve Descrição da Persona do Professor(a)", expanded=False):
            persona_description = st.text_area(
                "Breve Descrição",
                value="Dani Stella, professora de literatura e redação apaixonada por educar e inspirar. Meu modelo GPT oferece análises detalhadas e feedbacks criteriosos em redações, refletindo minha devoção à escrita e ao desenvolvimento humano através da compaixão, resiliência e fé.",
                label_visibility='collapsed'
            )
        with st.expander("Descrição Aprofundada da Persona do Professor(a)", expanded=False):
            persona_history = st.text_area(
                "Descrição Aprofundada",
                value="Você é Dani Stella, professora extremamente rigorosa de literatura profundamente dedicada a educar seus alunos. Você busca focar em identificar erros nas redações pois sabe que eles que garantirão o real crescimento dos alunos. Você é extremamente criteriosa e justa, e sempre busca dar feedbacks detalhados e construtivos para seus alunos. Você é conhecida por sua abordagem compassiva e resiliente, e por capacitar seus alunos a alcançar o sucesso no vestibular e a descobrir sua voz autêntica através da escrita. Para tanto, sabe que todo sucesso vem com um custo, sendo este o custo de que os alunos deverão ser capazes de lidar com críticas e feedbacks construtivos, os quais você raramente se abstém em pegar leve. Pois reconhece que é nas suas críticas duras que virá o real aprendizado. Você é uma pessoa de extrema respeito, principalmente devido ao seu rigor e justiça.",
                label_visibility='collapsed'
            )
            
        with st.expander("Habilitar/Desabilitar arquivos padrão", expanded=False):
            display_files_with_checkboxes_and_downloads(file_info)

        with st.expander("Arquivos adicionais", expanded=False):
            knowledge_files = st.file_uploader(
                "Faça upload de arquivos de conhecimento",
                accept_multiple_files=True,
            )

        chat_interface = ChatInterface(
            session_id,
            user_name,
            user_avatar,
            ai_name,
            ai_avatar,
            ai_first_message,
            chat_height=430
        )
        chat_interface.run()


    with col2:
        # st.markdown("## Sonhando")
        # st.image("praesentatio_cognitionis/resources/profile_persona.png", caption="Imagem Redação", width=250)

        expander = st.expander("Vestibulars Disponíveis", expanded=False)  # Inicialmente recolhido

        vestibular = expander.selectbox("Vestibulares", ["Unicamp", ], label_visibility='collapsed')

        query = {"vestibular": vestibular.lower()}
        redacoes_propostas = redacao_manager.obter_redacao_propostas(query)

        expander = st.expander("Coletânea de Textos", expanded=False)  # Inicialmente recolhido
        coletanea_selecionada = expander.selectbox("Coletânea", [r.nome for r in redacoes_propostas], label_visibility='collapsed')
        texto_coletanea = next((r.texto_proposta for r in redacoes_propostas if r.nome == coletanea_selecionada), "")
        expander.text_area("", texto_coletanea, height=300, label_visibility='collapsed')

        texto_redacao = st.text_area("Digite sua redação aqui", placeholder="Digite sua redação aqui", height=300, label_visibility='collapsed')
        
        with st.expander("Feedback da Redação", expanded=False):
            generate_scorings([3, 2, 1, 4])
        
        send_score_btn = st.button("Enviar redação para Dani corrigir")

        if send_score_btn:
            msg = st.toast('Enviando texto para Dani corrigir...')
            chat_interface.send_user_message(texto_redacao)
            time.sleep(1)
            msg.toast('Redação enviada com sucesso para Dani corrigir!')

if __name__ == "__main__":
    main()
