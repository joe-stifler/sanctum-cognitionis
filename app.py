# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_interface import ChatInterface
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms import LLMFamily
from servitium_cognitionis.llms import LLMGeminiModels
from servitium_cognitionis.connectors.csv_connector import CSVConnector
from servitium_cognitionis.managers.redacao_manager import RedacaoManager
from servitium_cognitionis.data_access.data_interface import DataInterface

# module imports from the standard python environment
import os
import time
import json
import vertexai
import replicate
import google.auth
import streamlit as st

# API Tokens and endpoints from `.streamlit/secrets.toml` file
os.environ["REPLICATE_API_TOKEN"] = st.secrets["IMAGE_GENERATION"]["REPLICATE_API_TOKEN"]
REPLICATE_MODEL_ENDPOINTSTABILITY = st.secrets["IMAGE_GENERATION"]["REPLICATE_MODEL_ENDPOINTSTABILITY"]

# def check_password():
#     """Returns `True` if the user had a correct password."""

#     def login_form():
#         """Form with widgets to collect user information"""
#         with st.form("Credentials"):
#             st.text_input("Username", key="username")
#             st.text_input("Password", type="password", key="password")
#             st.form_submit_button("Log in", on_click=password_entered)

#     def password_entered():
#         """Checks whether a password entered by the user is correct."""
#         if st.session_state["username"] in st.secrets[
#             "passwords"
#         ] and hmac.compare_digest(
#             st.session_state["password"],
#             st.secrets.passwords[st.session_state["username"]],
#         ):
#             st.session_state["password_correct"] = True
#             del st.session_state["password"]  # Don't store the username or password.
#             del st.session_state["username"]
#         else:
#             st.session_state["password_correct"] = False

#     # Return True if the username + password is validated.
#     if st.session_state.get("password_correct", False):
#         return True

#     # Show inputs for username + password.
#     login_form()
#     if "password_correct" in st.session_state:
#         st.error("😕 User not known or password incorrect")
#     return False


# if not check_password():
#     st.stop()

########################################################################################

def setup_data_access():
    table_mappings = {
        'redacoes_candidatos': 'databases/redacao/unicamp/unicamp_redacoes_candidatos.csv',
        'redacoes_propostas': 'databases/redacao/unicamp/unicamp_redacoes_propostas.csv'
    }
    csv_connector = CSVConnector(table_mappings)
    data_interface = DataInterface({'csv': csv_connector})
    return data_interface

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
    st.write("Base de conhecimento do professor(a):")
    
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
        'databases/redacao/unicamp/unicamp_redacoes_candidatos.json',
        'personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md',
        'personas/professores/redacao/dani-stella/definicao_de_plagio.md',
        'databases/redacao/unicamp/unicamp_redacoes_propostas.json',
        'personas/professores/redacao/dani-stella/a_redacao_na_unicamp.md',
    ]

    with st.expander("Configure seu professor(a)", expanded=False):
        def on_change_persona_name():
            st.session_state["persona_settings"]["persona_name"] = st.session_state.new_persona_name

        st.text_input(
            "Nome do professor(a):",
            st.session_state["persona_settings"]["persona_name"],
            on_change=on_change_persona_name,
            key='new_persona_name'
        )
        
        def on_change_persona_description():
            st.session_state["persona_settings"]["persona_description"] = st.session_state.new_persona_description

        st.text_area(
            "Descrição do professor(a):",
            value=st.session_state["persona_settings"]["persona_description"],
            on_change=on_change_persona_description,
            key='new_persona_description'
        )

        def change_files_state():
            st.session_state["persona_settings"]["persona_files"] = list(st.session_state.new_persona_files)

        st.multiselect(
            'Base de conhecimento do professor(a):',
            available_files,
            default=st.session_state["persona_settings"]["persona_files"],
            on_change=change_files_state,
            key="new_persona_files"
        )

        st.warning("Não se esqueça de clicar no botão 'Atualizar Professor(a)' acima para aplicar quaisquer mudanças.")
        st.warning("Tome apenas cuidado, pois atualizar o professor(a) levará a uma perca completa do histórico de conversa atual.")

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
    
    return coletanea_escolhida


def essay_writing_layout(height_main_containers):
    with st.form("my_form2"):
        texto_redacao = st.text_area("Digite sua redação aqui", placeholder="Digite sua redação aqui", height=int(1.155 * height_main_containers), label_visibility='collapsed')
        submitted = st.form_submit_button(
            "Submeter para avaliação", use_container_width=True)

    return submitted, texto_redacao

def specific_stable_diffusion_settings_layout():
    with st.expander("**Configure a geração de imagem**"):
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
    
    with st.expander("Gere uma nova imagem", expanded=False):
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
def stable_diffusion_layout(submitted, *args):
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
    with st.expander("Configure o modelo de inteligência artificial", expanded=False):
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
            index=llm_family.current_model_index(),
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

        st.warning("Não se esqueça de clicar no botão 'Atualizar Professor(a)' acima para aplicar quaisquer mudanças.")
        st.warning("Tome apenas cuidado, pois atualizar o professor(a) levará a uma perca completa do histórico de conversa atual.")


def reset_ai_chat(chat_interface, send_initial_message=True):
    chat_interface.reset_ai_chat(
        **{
            "persona_name": st.session_state["persona_settings"]["persona_name"],
            "persona_description": st.session_state["persona_settings"]["persona_description"],
            "persona_files": st.session_state["persona_settings"]["persona_files"],
            "llm_family": st.session_state["llm_families"][st.session_state["chosen_llm_family"]],
            "send_initial_message": send_initial_message,
        }
    )

@st.cache_resource
def get_redacao_manager():
    print("Creating RedacaoManager")
    redacao_manager = RedacaoManager(
        dal=setup_data_access(),
        tabela_redacoes_propostas='redacoes_propostas',
        tabela_redacoes_aluno='redacoes_aluno',
        tabela_redacoes_candidatos='redacoes_candidatos'
    )
    return redacao_manager

@st.cache_resource
def get_chat_interface():
    print("Creating ChatInterface")
    chat_interface = ChatInterface(
        session_id="redacoes",
        user_name=":blue[estudante]",
        user_avatar="👩🏾‍🎓",
        chat_height=400
    )
    reset_ai_chat(chat_interface, send_initial_message=False)
    return chat_interface


def maybe_st_initialize_state():
    if "llm_families" not in st.session_state:
        st.session_state["llm_families"] = {
            str(family.value): family.value for family in LLMFamily
        }
        st.session_state["chosen_llm_family"] = str(LLMFamily.VERTEXAI_GEMINI)

    if "persona_settings" not in st.session_state:
        default_persona_description_path = 'personas/professores/redacao/dani-stella/persona_dani_stella.md'

        with open(default_persona_description_path, 'r', encoding='utf-8') as file:
            default_persona_description = file.read()

        st.session_state["persona_settings"] = {
            "persona_name": "Dani Stella",
            "persona_files": [
                "databases/redacao/unicamp/unicamp_redacoes_candidatos.json",
                "personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md",
                #"personas/professores/redacao/dani-stella/definicao_de_plagio.md",
                "databases/redacao/unicamp/unicamp_redacoes_propostas.json",
                "personas/professores/redacao/dani-stella/a_redacao_na_unicamp.md",
            ],
            
            "persona_description": default_persona_description
        }

    key_path = ".streamlit/google_secrets.json"

    if "created_google_json" not in st.session_state:
        st.session_state["created_google_json"] = True

        if not os.path.exists(".streamlit"):
            os.makedirs(".streamlit")

        with open(key_path, "w", encoding='utf-8') as file:
            file.write(st.secrets["VERTEXAI"]["GOOGLE_JSON_SECRETS"])

        time.sleep(0.1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path


def main():
    maybe_st_initialize_state()

    gemini_cloud_location = st.secrets["VERTEXAI"]["GEMINI_CLOUD_LOCATION"]

    _, project_id = google.auth.default()

    vertexai.init(project=project_id, location=gemini_cloud_location)

    height_main_containers = 400
    chat_interface = get_chat_interface()
    redacao_manager = get_redacao_manager()

    st.markdown("<h1 style='text-align: center;'>📚 Página de Redações 📚</h1>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([2, 3, 1.5], gap="large")

    with col1:
        coletanea_escolhida = select_essay_layout(redacao_manager)

        submitted, texto_redacao = essay_writing_layout(height_main_containers)

        if submitted:
            st.toast('Redação sendo enviada para avaliação...')

            context_mensagem = (
                f"## Ano do Vestibular:\n\n{coletanea_escolhida.ano_vestibular}\n\n"
                f"## Proposta Escolhida:\n\n{coletanea_escolhida.numero_proposta}\n\n"
                f"---------------------------------------------------------\n\n"
                f"## Redação do Aluno:\n\n"
            )

            chat_interface.send_user_message(texto_redacao, prefix_message_context=context_mensagem)

    with col2:
        chat_interface.setup_layout()

    with col3:
        update_persona = st.button(
            "Atualizar Professor(a)",
            use_container_width=True,
            on_click=reset_ai_chat,
            args=[chat_interface, ]
        )

        update_persona_layout()

        llm_family_model_layout()

        if not update_persona:
            chat_interface.run()

        image_container = st.container(border=True, height=int(0.76 * height_main_containers))
        submitted = stable_diffusion_prompt_form_layout()
        specific_stable_diffusion_params = specific_stable_diffusion_settings_layout()

        with image_container:
            stable_diffusion_layout(submitted, *specific_stable_diffusion_params)

if __name__ == "__main__":
    main()
