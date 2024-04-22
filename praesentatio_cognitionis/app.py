import time
import streamlit as st

import replicate
import requests
import io
import zipfile

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
        'redacoes_candidatos': 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
        'redacoes_propostas': 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv'
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
    default_files_enabled = {}
    for file_label, file_path, file_enabled in file_info:
        # Create two columns: one for the checkbox, one for the download button
        col1, col2 = st.columns([1, 2])

        # In the first column, display the checkbox
        with col1:
            checkbox_label = f"Enable download for {file_label}"
            is_checked = st.checkbox(checkbox_label, value=file_enabled, key=f"checkbox_{file_label}")
            default_files_enabled[file_path] = is_checked

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

def update_persona_layout(file_info):
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

    if st.button("Atualizar persona do professor(a)"):
        st.write("Persona do professor(a) atualizada com sucesso!")

# def text_submission_layout(redacao_manager):
#     # ... existing text submission and feedback code ...

def chat_interface_layout():
    session_id = "redacoes"
    user_name = "estudante"
    user_avatar = "👩🏾‍🎓"
    ai_name = "professor"
    ai_avatar = "👩🏽‍🏫"
    ai_first_message = "Olá! Meu nome é Dani Stella, como posso te ajudar?"
    
    file_info = [
        ("redacoes_aluno.csv", 'databases/redacao/unicamp/unicamp_redacoes_aluno.csv', False),
        ("unicamp_redacoes_candidatos.csv", 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv', True),
        ("unicamp_redacoes_propostas.csv", 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv', True),
        ("grade_de_correcao_analitica_unicamp.txt", 'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt', True)
    ]

    # st.image("praesentatio_cognitionis/resources/profile_persona.png", caption="Imagem Redação", width=250)
    
    with st.container(border=True):
        update_persona_layout(file_info)
    

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
    
    return chat_interface

def essay_writing_layout(redacao_manager, chat_interface):
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
        generate_scorings([0, 0, 0, 0])
    
    send_score_btn = st.button("Enviar redação para Dani corrigir")

    if send_score_btn:
        msg = st.toast('Enviando texto para Dani corrigir...')
        chat_interface.send_user_message(texto_redacao)
        time.sleep(1)
        msg.toast('Redação enviada com sucesso para Dani corrigir!')

# Define the function to generate images based on text prompts
def generate_images_container():
    with st.container():
        # UI for text prompts and other parameters
        st.markdown("## :art: Generate Your Art")
        with st.form("image_gen_form", clear_on_submit=True):
            prompt = st.text_area("Enter a description for the art you want to create:", height=150)
            num_images = st.number_input('Number of images to generate', min_value=1, max_value=4, value=1)
            submit_button = st.form_submit_button(label='Generate Images')

            if submit_button and prompt:
                # Make API call to generate images
                response = replicate.predictions.create(
                    version='YOUR_MODEL_VERSION',
                    input={'prompt': prompt, 'num_images': num_images}
                )

                # Display generated images or handle errors
                if response['status'] == 'succeeded':
                    # Assuming the response contains the URLs of generated images
                    images = response['output']
                    st.image(images, width=300, caption=["Generated Image"] * len(images))
                elif response['status'] == 'failed':
                    st.error("Image generation failed. Please try again.")
                else:
                    st.warning("Image generation in progress...")

                # Optional: Provide download for generated images as a zip file
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, img_url in enumerate(images, start=1):
                        img_data = requests.get(img_url).content
                        zip_file.writestr(f"image_{i}.png", img_data)
                zip_buffer.seek(0)
                st.download_button(
                    label="Download Generated Images",
                    data=zip_buffer,
                    file_name="generated_images.zip",
                    mime="application/zip"
                )

def main():
    dal = setup_data_access()
    redacao_manager = RedacaoManager(
        dal=dal,
        tabela_redacoes_propostas='redacoes_propostas',
        tabela_redacoes_aluno='redacoes_aluno',
        tabela_redacoes_candidatos='redacoes_candidatos',
        redacao_class=RedacaoCandidatoUnicamp
    )

    st.markdown("<h1 style='text-align: center;'>📚 Página de Redações 📚</h1>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        chat_interface = chat_interface_layout()

    with col2:
        essay_writing_layout(redacao_manager, chat_interface)
        generate_images_container()

if __name__ == "__main__":
    main()
