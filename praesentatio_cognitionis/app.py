# module imports from the praesentatio_cognitionis package
from chat_interface import ChatInterface

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms import LLMFamily
from servitium_cognitionis.connectors.csv_connector import CSVConnector
from servitium_cognitionis.managers.redacao_manager import RedacaoManager
from servitium_cognitionis.data_access.data_interface import DataInterface

# module imports from the standard python environment
import os
import time
import vertexai
import replicate
import streamlit as st
import plotly.graph_objects as go

from header import show_header
show_header(0)


# API Tokens and endpoints from `.streamlit/secrets.toml` file
os.environ["REPLICATE_API_TOKEN"] = st.secrets["IMAGE_GENERATION"]["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["IMAGE_GENERATION"]["REPLICATE_MODEL_ENDPOINTSTABILITY"]


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

def display_files_with_checkboxes_and_downloads(temp_persona_files):
    st.write("Arquivos disponíveis na base de conhecimento da persona:")
    
    # Create two columns: one for the checkbox, one for the download button
    with st.container(border=True):
        col1, col2 = st.columns([1, 1])

        for idx, persona_file in enumerate(temp_persona_files.items()):
            chosen_col = col1 if idx % 2 == 0 else col2

            file_path, file_enabled = persona_file
            file_label = os.path.basename(file_path)

            with chosen_col:
                checkbox_label = f"`Usar {file_label}?`"
                is_checked = st.checkbox(checkbox_label, value=file_enabled, key=f"checkbox_{file_label}")
                temp_persona_files[file_path] = is_checked

def update_persona_layout():
    available_files = [
        'databases/redacao/unicamp/unicamp_redacoes_aluno.csv',
        'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
        'databases/redacao/unicamp/unicamp_redacoes_propostas.csv',
        'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt',
        'personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md',
    ]
    
    if "persona_settings" not in st.session_state:
        st.session_state["persona_settings"] = {
            "persona_name": "Dani Stella: Mentora de Redação Unicamp",
            
            "persona_description": """Dani Stella, professora de literatura e redação apaixonada por educar e inspirar. Meu modelo GPT oferece análises detalhadas e feedbacks criteriosos em redações, refletindo minha devoção à escrita e ao desenvolvimento humano através da compaixão, resiliência e fé.

                Você é Dani Stella, professora extremamente rigorosa de literatura profundamente dedicada a educar seus alunos. Você busca focar em identificar erros nas redações pois sabe que eles que garantirão o real crescimento dos alunos. Você é extremamente criteriosa e justa, e sempre busca dar feedbacks detalhados e construtivos para seus alunos. Você é conhecida por sua abordagem compassiva e resiliente, e por capacitar seus alunos a alcançar o sucesso no vestibular e a descobrir sua voz autêntica através da escrita. Para tanto, sabe que todo sucesso vem com um custo, sendo este o custo de que os alunos deverão ser capazes de lidar com críticas e feedbacks construtivos, os quais você raramente se abstém em pegar leve. Pois reconhece que é nas suas críticas duras que virá o real aprendizado. Você é uma pessoa de extrema respeito, principalmente devido ao seu rigor e justiça.
            """,

            "persona_files": [
                'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
                'databases/redacao/unicamp/unicamp_redacoes_propostas.csv',
                'personas/professores/redacao/dani-stella/grade_de_correcao_analitica_unicamp.txt',
            ]
        }

        st.session_state["temporary_persona_settings"] = st.session_state["persona_settings"]

    with st.expander("Configurações da persona do professor(a)", expanded=False):
        def on_change_persona_name():
            st.session_state["temporary_persona_settings"]["persona_name"] = st.session_state.new_persona_name

        st.text_input(
            "Nome da persona do professor(a):",
            st.session_state["temporary_persona_settings"]["persona_name"],
            on_change=on_change_persona_name,
            key='new_persona_name'
        )
        
        def on_change_persona_description():
            st.session_state["temporary_persona_settings"]["persona_description"] = st.session_state.new_persona_description

        st.text_area(
            "Descrição da persona do professor(a):",
            value=st.session_state["temporary_persona_settings"]["persona_description"],
            on_change=on_change_persona_description,
            key='new_persona_description'
        )

        def change_files_state():
            st.session_state["temporary_persona_settings"]["persona_files"] = list(st.session_state.new_persona_files)

        st.multiselect(
            'Arquivos disponíveis na base de conhecimento da persona:',
            available_files,
            default=st.session_state["temporary_persona_settings"]["persona_files"],
            on_change=change_files_state,
            key="new_persona_files"
        )

        st.error("Tome cuidado! Atualizar a persona irá excluir o histórico de conversas atual.")

        def on_click_update_persona():
            st.session_state["temporary_persona_settings"] = st.session_state["persona_settings"]
            st.toast("Configurações da persona atualizadas com sucesso!")

        st.button("Atualizar Persona", use_container_width=True, on_click=on_click_update_persona)

def chat_interface_layout(height_main_containers):
    session_id = "redacoes"
    user_name = "estudante"
    user_avatar = "👩🏾‍🎓"
    ai_name = "professor"
    ai_avatar = "👩🏽‍🏫"
    ai_first_message = "Olá! Meu nome é Dani Stella, como posso te ajudar?"

    chat_interface = ChatInterface(
        session_id,
        user_name,
        user_avatar,
        ai_name,
        ai_avatar,
        ai_first_message,
        chat_height=height_main_containers
    )
    chat_interface.run()
    
    return chat_interface

def select_essay_layout(redacao_manager):
    expander = st.expander("Redações Disponíveis", expanded=False)

    vestibular = expander.selectbox("Escolha o vestibular", ["Unicamp", ])
    redacoes_propostas = redacao_manager.obter_redacao_propostas(
        vestibular,
        query = {
            'order_by': ['ano_vestibular', 'numero_proposta'],
            'ascending': [False, True]
        }
    )

    coletanea_escolhida = expander.selectbox(
        "Escolha a proposta e ano do vestibular",
        redacoes_propostas,
        format_func=lambda r: f"{r.nome}",
    )

    expander.text_area(
        "Coletânea de textos",
        coletanea_escolhida.texto_proposta,
        height=300,
        label_visibility='collapsed',
        disabled=True
    )


def essay_writing_layout(height_main_containers):
    with st.expander("Feedback da Redação", expanded=False):
        generate_scorings([0, 0, 0, 0])

    with st.form("my_form2"):
        texto_redacao = st.text_area("Digite sua redação aqui", placeholder="Digite sua redação aqui", height=height_main_containers, label_visibility='collapsed')
        submitted = st.form_submit_button(
            "Submeter para avaliação", use_container_width=True)

    return submitted, texto_redacao

def specific_stable_diffusion_settings_layout():
    with st.expander("**Melhore sua imagem gerada**"):
        width = st.number_input("Largura da imagem gerada", value=1024)
        height = st.number_input("Altura da imagem gerada", value=1024)
        scheduler = st.selectbox('Scheduler', ('K_EULER', 'DDIM', 'DPMSolverMultistep', 'HeunDiscrete',
                                                'KarrasDPM', 'K_EULER_ANCESTRAL', 'PNDM'))
        num_inference_steps = st.slider(
            "Número de etapas de remoção de ruído", value=4, min_value=1, max_value=10)
        guidance_scale = st.slider(
            "Escala para orientação sem classificador", value=0.0, min_value=0.0, max_value=50.0, step=0.1)
        prompt_strength = st.slider(
            "Força do prompt ao usar img2img/inpaint (1.0 corresponde à destruição total das informações na imagem)", value=0.8, max_value=1.0, step=0.1)
        refine = st.selectbox(
            "Selecione o estilo refinado a ser usado (deixe os outros 2 de fora)", ("expert_ensemble_refiner", "None"))
        high_noise_frac = st.slider(
            "Fração de ruído a ser usada para `expert_ensemble_refiner`", value=0.8, max_value=1.0, step=0.1)
        negative_prompt = st.text_area("**Quais elementos indesejados você não quer na imagem?**",
                                        value="the absolute worst quality, distorted features",
                                        help="Este é um prompt negativo, basicamente digite o que você não quer ver na imagem gerada")

    return width, height, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, negative_prompt

def stable_diffusion_prompt_form_layout() -> None:
    if "image_prompt" not in st.session_state:
        st.session_state["image_prompt"] = """In a fantastical scene, a creature with a human head and deer body emanates a green light."""
    
    with st.expander("Prompt para gerar imagem", expanded=False):
        def on_change_prompt():
            st.session_state["image_prompt"] = st.session_state.new_prompt

        st.text_area(
            "**Comece a escrever, Machado de Assis ✍🏾**",
            value=st.session_state["image_prompt"],
            help="Escreva um prompt para gerar uma imagem criativa",
            label_visibility='collapsed',
            on_change=on_change_prompt,
            key='new_prompt',
        )

        submitted = st.button(
            "Gerar uma imagem a partir do texto abaixo", use_container_width=True)

    return submitted

# Define the function to generate images based on text prompts
def stable_diffusion_layout(height_main_containers, submitted, *args):
    width, height, scheduler, num_inference_steps, guidance_scale, prompt_strength, refine, high_noise_frac, negative_prompt = args
    
    if "image_output" not in st.session_state:
        st.session_state["image_output"] = "praesentatio_cognitionis/resources/stable_diffusion_sample.png"

    generated_images_placeholder = st.empty()
    generated_images_placeholder.image(
        st.session_state["image_output"],
        caption=st.session_state["image_prompt"],
        use_column_width=True
    )

    if submitted:
        try:
            # Only call the API if the "Submit" button was pressed
            if submitted:
                with st.spinner('Gerando imagem...'):
                    # Calling the replicate API to get the image
                    with generated_images_placeholder.container():
                        output = replicate.run(
                            REPLICATE_MODEL_ENDPOINTSTABILITY,
                            input={
                                "prompt": st.session_state["image_prompt"],
                                "width": width,
                                "height": height,
                                "num_outputs": 1,
                                "scheduler": scheduler,
                                "num_inference_steps": num_inference_steps,
                                "guidance_scale": guidance_scale,
                                "prompt_stregth": prompt_strength,
                                "refine": refine,
                                "high_noise_frac": high_noise_frac,
                                "negative_prompt": negative_prompt
                            }
                        )

                        if output:
                            st.image(
                                output,
                                use_column_width=True,
                                caption=st.session_state["image_prompt"],
                                output_format="auto"
                            )
                            st.session_state["image_output"] = output
        except Exception as e:
            st.error(f'Encountered an error: {e}', icon="🚨")

def llm_family_model_layout():
    if "llm_families" not in st.session_state:
        st.session_state["llm_families"] = {
            str(family.value): family.value for family in LLMFamily
        }
        st.session_state["chosen_llm_family"] = str(LLMFamily.VERTEXAI_GEMINI)

    with st.expander("Provedor de inteligência artificial", expanded=False):
        def on_change_llm_family():
            st.session_state["chosen_llm_family"] = st.session_state.new_llm_family_name
        
        st.selectbox(
            'Escolha seu provedor de inteligência artificial',
            st.session_state["llm_families"].keys(),
            on_change=on_change_llm_family,
            key='new_llm_family_name'
        )
        
        llm_family_name = st.session_state["chosen_llm_family"]
        llm_family = st.session_state["llm_families"][llm_family_name]
        
        def on_change_llm_model():
            llm_family.update_current_model_name(st.session_state.new_llm_model_name)

        llm_model_name = st.selectbox(
            'Escolha seu modelo de inteligência artificial',
            llm_family.available_model_names(),
            on_change=on_change_llm_model,
            key='new_llm_model_name'
        )
        
        llm_model = llm_family.get_available_model(llm_model_name)
        
        def on_change_update_llm_model():
            llm_model.temperature = st.session_state.new_model_temperature

        st.slider(
            'Temperatura',
            min_value=llm_model.temperature_range[0],
            max_value=llm_model.temperature_range[1],
            value=llm_model.temperature,
            on_change=on_change_update_llm_model,
            key='new_model_temperature'
        )
        
        def on_change_update_llm_max_output_tokens():
            llm_model.max_output_tokens = st.session_state.new_max_output_tokens

        st.slider(
            'Número máximo de tokens de saída',
            min_value=llm_model.output_tokens_range[0],
            max_value=llm_model.output_tokens_range[1],
            value=llm_model.max_output_tokens,
            on_change=on_change_update_llm_max_output_tokens,
            key='new_max_output_tokens'
        )

def main():
    GEMINI_CLOUD_LOCATION = st.secrets["VERTEXAI"]["GEMINI_CLOUD_LOCATION"]
    GEMINI_CLOUD_PROJECT_ID = st.secrets["VERTEXAI"]["GEMINI_CLOUD_PROJECT_ID"]
    vertexai.init(project=GEMINI_CLOUD_PROJECT_ID, location=GEMINI_CLOUD_LOCATION)

    dal = setup_data_access()
    redacao_manager = RedacaoManager(
        dal=dal,
        tabela_redacoes_propostas='redacoes_propostas',
        tabela_redacoes_aluno='redacoes_aluno',
        tabela_redacoes_candidatos='redacoes_candidatos'
    )

    st.markdown("<h1 style='text-align: center;'>📚 Página de Redações 📚</h1>", unsafe_allow_html=True)
    st.divider()

    height_main_containers = 400
    col1, col2, col3 = st.columns([1, 1, 0.6], gap="large")

    with col1:
        select_essay_layout(redacao_manager)

        submitted, texto_redacao = essay_writing_layout(height_main_containers)

    with col2:
        llm_family_model_layout()

        update_persona_layout()

        chat_interface = chat_interface_layout(height_main_containers)

        if submitted:
            st.toast('Redação enviada com sucesso para Dani corrigir!')
            chat_interface.send_user_message(texto_redacao)

    with col3:
        specific_stable_diffusion_params = specific_stable_diffusion_settings_layout()

        submitted = stable_diffusion_prompt_form_layout()

        with st.container(border=True):
            stable_diffusion_layout(int(0.8 * height_main_containers), submitted, *specific_stable_diffusion_params)

if __name__ == "__main__":
    main()
