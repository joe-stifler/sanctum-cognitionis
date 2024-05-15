# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_connector import ChatConnector
from praesentatio_cognitionis.streamlit_file_handler import StreamlitFileHandler
from praesentatio_cognitionis.files import (
    PandasFile, PDFFile, AudioFile, ImageFile, TextFile, JsonFile, CodeFile, VideoFile
)
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.mock import LLMMockFamily
from servitium_cognitionis.llms.gemini import GeminiDevFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the notion_indexer
from notion_indexer.database_node import DatabaseNode
from notion_indexer.notion_reader import NotionReader

# module imports from the standard python environment
import os
import io
import time
import uuid
import zipfile
import logging
import datetime
import traceback
import streamlit as st
import google.generativeai as genai
from streamlit_extras.row import row
from streamlit_pdf_viewer import pdf_viewer
from streamlit_feedback import streamlit_feedback
from streamlit_extras.stylable_container import stylable_container

@st.cache_data
def setup_logger():
    # Get log ID
    log_dir = "logs"
    log_name = st.session_state.get('log_name', '')

    # Generate unique log file name including log ID and creation date
    if not log_name:
        log_id = str(uuid.uuid4().hex)
        creation_date = datetime.datetime.now().strftime("date_%Y-%m-%d_time_%H-%M-%S")
        log_name = f"{log_dir}/{creation_date}_log_id_{log_id}.log"
        st.session_state['log_name'] = log_name

    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum level of messages to log

    # Create handlers for stdout and file
    c_handler = logging.StreamHandler()  # Console handler
    f_handler = logging.FileHandler(st.session_state['log_name'], mode='w')  # File handler
    c_handler.setLevel(logging.INFO)  # Level for console handler
    f_handler.setLevel(logging.DEBUG)  # Level for file handler

    # Create formatters and add them to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

logger = setup_logger()

pc = st.get_option('theme.primaryColor')
bc = st.get_option('theme.backgroundColor')
sbc = st.get_option('theme.secondaryBackgroundColor')
tc = st.get_option('theme.textColor')

################################################################################

def maybe_st_initialize_state():
    if "persona_settings_path" not in st.session_state:
        # st.session_state["persona_settings_path"] = "dados/personas/professores/redacao/dani-stella/persona_config.json"
        st.session_state["persona_settings_path"] = "dados/personas/empty/persona_config.json"

        logger.info("Setting persona settings path to: %s", st.session_state["persona_settings_path"])


def get_ai_chat():
    creativity_level = 1.0
    speech_conciseness = 2048
    thought_process = "Intuitivo"
    llm_model_default_name = "GeminiDevModelPro1_5"
    llm_family_name = st.session_state.get("LLM_FAMILY", "GeminiDevFamily")

    if llm_family_name == "GeminiDevFamily":
        llm_family = GeminiDevFamily()
        logger.info("Using GeminiDevFamily")
    elif llm_family_name == "LLMMockFamily":
        llm_family = LLMMockFamily()
        logger.info("Using LLMMockFamily")

    llm_model_name = st.session_state.get("llm_model_name", llm_model_default_name)

    persona_name = st.session_state.get("persona_name", "Zoid")
    thought_process = st.session_state.get("thought_process", thought_process)
    creativity_level = st.session_state.get("creativity_level", creativity_level)
    speech_conciseness = st.session_state.get("speech_conciseness", speech_conciseness)

    # change llm_family to LLMMockFamily in case FORCE_LLM_MOCK_FAMILY is set in the env var
    if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
        llm_family = LLMMockFamily()
        logger.info("Using LLMMockFamily as the LLM family due to the FORCE_LLM_MOCK_FAMILY env var.")

    persona = Persona(
        name=persona_name,
        creativity_level=creativity_level,
        speech_conciseness=speech_conciseness,
        persona_description="",
        thought_process=thought_process,
    )

    llm_model = llm_family.get_model(llm_model_name)

    return llm_model, persona

@st.cache_resource
def create_chat_connector():
    logger.info("Creating chat connector")
    return ChatConnector()

def write_medatada_chat_message(role, files):
    if len(files) == 0:
        return

    if role == "assistant":
        num_cols = min(3, len(files))

        # check if there are any arguments
        if sum([len(arguments) for arguments in files]) == 0:
            return

        if not os.environ.get("FORCE_LLM_MOCK_FAMILY"):
            return

        with st.expander("**Metadados da resposta**", expanded=False):
            cols = st.columns(num_cols)

            for idx, arguments in enumerate(files):
                if len(arguments) > 0:
                    with cols[idx % num_cols]:
                        st.divider()
                        st.json(arguments)
        return

    for idx, file in enumerate(files):
        with st.expander(f"**{file.name}:**", expanded=False):
            if isinstance(file, ImageFile):
                st.image(file.content, caption=file.name)
            elif isinstance(file, PDFFile):
                pdf_viewer(file.content, height=600, key=f"pdf_{st.session_state['counter']}_{idx}")
            elif isinstance(file, TextFile):
                st.markdown(file.content)
            elif isinstance(file, AudioFile):
                st.audio(file.content, format=file.mime_type)
            elif isinstance(file, JsonFile):
                st.json(file.content)
            elif isinstance(file, PandasFile):
                st.dataframe(file.content)
            elif isinstance(file, CodeFile):
                st.code(file.content, language="python")
            elif isinstance(file, VideoFile):
                st.video(file.content, format=file.mime_type)
            else:
                st.error(f"Arquivo não suportado: {file.name}")

def chat_messages(chat_connector, user_input_message, user_uploaded_files):
    # Initialize or fetch existing chat history
    if "session_id" not in st.session_state:
        llm_model, persona = get_ai_chat()
        logger.info("Chosen Persona: %s", persona)
        logger.info("Chosen LLM Model: %s", llm_model)
        chat_history = chat_connector.create_chat_history()
        chat_history.initialize_chat_message(llm_model, persona)
        logger.info("Creating chat history with session_id: %s", chat_history.session_id)
        st.session_state["session_id"] = chat_history.session_id
    else:
        chat_history = chat_connector.fetch_chat_history(st.session_state["session_id"])
        llm_model = chat_history.get_llm_model()
        persona = chat_history.get_persona()

    warning_message = "⚠️ Defina sua chave de API na barra lateral esquerda antes de iniciar a conversa."

    if not st.session_state["api_token_value"]:
        st.warning(warning_message)
        st.toast(warning_message)
        return

    info_columns = st.columns(2)
    info_columns[0].info(f"""🤖 **Nome:** {persona.name}\n\n""")
    info_columns[1].info(f"""**Pensamento:** {persona.thought_process}\n\n""")

    # Display past messages from chat history
    if chat_history:
        for chat_message in chat_history.chat_messages:
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(":blue[Usuário]")
                st.write(chat_message.user_message)
                write_medatada_chat_message("user", chat_message.user_uploaded_files)

            with st.chat_message("assistant", avatar="🤖"):
                st.write(f":red[{chat_message.ai_name}]")
                st.write(''.join(chat_message.ai_messages))

                if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
                    write_medatada_chat_message("assistant", chat_message.ai_extra_args)

    if user_input_message:
        try:
            if not st.session_state["api_token_value"]:
                st.warning(warning_message)
                return

            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(f":blue[Usuário]")
                st.write(user_input_message)
                write_medatada_chat_message("usuario", user_uploaded_files)

            logger.debug("Sending user message:\n\n```text\n%s\n```", user_input_message)

            # Display AI responses
            with st.spinner("Estou processando sua mensagem..."):
                # Send user message to AI inference
                new_chat_message = chat_history.send_ai_message(
                    user_input_message, user_uploaded_files
                )

                with st.chat_message("assistant", avatar="🤖"):
                    st.write(f":red[{chat_history.get_persona().name}]")

                    st.write_stream(new_chat_message.process_ai_messages())
                    logger.debug(f"AI new messages: \n\n{new_chat_message.ai_extra_args}")
                    logger.debug(f"\n\nAI new message kwargs: \n\n{new_chat_message.ai_extra_args}")
                    write_medatada_chat_message("assistant", new_chat_message.ai_extra_args)

                # feedback = streamlit_feedback(
                #     feedback_type="thumbs",
                #     optional_text_label="[Opcional] Por favor, forneça um feedback",
                #     align="flex-start",
                # )

        except FileNotFoundError as e:
            logger.error("Erro ao inicializar a persona: %s", str(e))
            st.error(f"Erro ao inicializar a persona: {e}")
        except Exception as e:
            error_str = str(e)

            error_details = traceback.format_exc()
            logger.error(f"Error processing user input: %s\nDetails: %s", error_str, error_details)

            if "400 API key not valid" in error_str:
                st.error("Erro ao inicializar o chat: API key inválida")
            else:
                st.error(f"Erro: {error_str}\nDetails: {error_details}")


def file_uploader_fragment(user_input_message):
    if "file_uploader_counter" not in st.session_state:
        st.session_state["file_uploader_counter"] = 0

    old_input_counter = st.session_state["file_uploader_counter"]
    files_container = st.empty()

    def create_file_uploader(file_uploader_id):
        file_uploader_key = f"file_uploader_{file_uploader_id}"

        return files_container.file_uploader(
            "Upload de arquivos",
            accept_multiple_files=True,
            key=file_uploader_key,
            label_visibility='collapsed',
            type=StreamlitFileHandler.SUPPORTED_FILE_TYPES,
        )

    old_user_uploaded_files = create_file_uploader(old_input_counter)

    if len(old_user_uploaded_files) > 0:
        old_user_uploaded_files.append(old_user_uploaded_files[-1])

    processed_files = []

    if user_input_message and len(user_input_message) > 0:
        # Convert the uploaded files to a standard format
        file_handler = StreamlitFileHandler(old_user_uploaded_files)
        processed_files = file_handler.process_files()

        st.session_state["file_uploader_counter"] += 1
        new_input_counter = st.session_state["file_uploader_counter"]
        create_file_uploader(new_input_counter)

    return processed_files

def model_settings():
    if "api_token_value" not in st.session_state:
        st.session_state["api_token_value"] = None

        if "GOOGLE_DEV" in st.secrets:
            st.session_state["thought_process"] = "Racional"
            st.session_state["speech_conciseness"] = 8192
            st.session_state["api_token_value"] = st.secrets["GOOGLE_DEV"]["GOOGLE_API_KEY"]

    if "creativity_level" not in st.session_state:
        st.session_state["creativity_level"] = 1.0

    if "speech_conciseness" not in st.session_state:
        st.session_state["speech_conciseness"] = 2048

    if "thought_process" not in st.session_state:
        st.session_state["thought_process"] = "Intuitivo"

    with st.sidebar:
        default_api_key = st.session_state["api_token_value"]
        default_creativity_level = st.session_state["creativity_level"]
        default_simple_llm_model_name = st.session_state["thought_process"]
        
        with st.expander("Configurações do modelo"):
            with st.container():
                st.session_state["LLM_FAMILY"] = "GeminiDevFamily"

                gemini_models = {
                    "Intuitivo": "GeminiDevModelPro1_0",
                    "Racional": "GeminiDevModelPro1_5",
                }
                gemini_models_list = list(gemini_models.keys())
                default_gemini_models_idx = gemini_models_list.index(default_simple_llm_model_name)

                def update_speech_conciseness(conciseness):
                    model_name = st.session_state["selectbox_llm_model_name"]

                    if model_name == "Intuitivo":
                        conciseness[0] = 0
                        conciseness[1] = 2048
                    elif model_name == "Racional":
                        conciseness[0] = 0
                        conciseness[1] = 8192

                    conciseness[2] = conciseness[1]

                conciseness = [0, 0, 0]

                simple_llm_model_name = st.selectbox(
                    "Processo de pensamento",
                    gemini_models_list,
                    index=default_gemini_models_idx,
                    on_change=update_speech_conciseness,
                    key="selectbox_llm_model_name",
                    args=(conciseness, )
                )
                update_speech_conciseness(conciseness)

                speech_conciseness = st.slider(
                    "Concisão (letras por resposta)",
                    min_value=conciseness[0],
                    max_value=conciseness[1],
                    value=conciseness[2],
                    step=128 * 4,
                    help=f"Utilize valores próximos de {conciseness[0]} para respostas mais curtas ou próximos de {conciseness[1]} para respostas mais longas."
                )

                creativity_level = st.slider(
                    "Nível de criatividade",
                    min_value=0.0,
                    max_value=1.0,
                    value=default_creativity_level,
                    step=0.1,
                    help="Utilize valores próximos de 0 para respostas mais diretas ou próximos de 1 para respostas mais criativas."
                )

                llm_model = gemini_models[simple_llm_model_name]

                api_key = st.text_input(
                    "API Token",
                    key="api_token",
                    type="password",
                    value=default_api_key
                )
                api_buttom = st.button("Atualizar")

            if api_buttom:
                if len(api_key) > 0:
                    st.session_state["api_token_value"] = api_key

                st.session_state["llm_model_name"] = llm_model
                st.session_state["creativity_level"] = creativity_level
                st.session_state["thought_process"] = simple_llm_model_name
                st.session_state["speech_conciseness"] = speech_conciseness

                if "session_id" in st.session_state:
                    del st.session_state["session_id"]

                st.rerun()

def setup_notion_indexing():
    with st.sidebar:
        with st.expander("Configuração do Notion"):
            if "notion_api_token" not in st.session_state:
                st.session_state["notion_api_token"] = None
                st.session_state["notion_profundidade"] = 1
                st.session_state["notion_numero_paginas"] = -1
                st.session_state["notion_filtros"] = ""
                st.session_state["notion_ordenacao"] = ""

                if "NOTION" in st.secrets:
                    st.session_state["notion_api_token"] = st.secrets["NOTION"]["NOTION_API_KEY"]

            default_api_key = st.session_state["notion_api_token"]
            profundidade_notion_atual = st.session_state["notion_profundidade"]
            numero_paginas_notion_atual = st.session_state["notion_numero_paginas"]

            profundidade = st.number_input(
                "Profundidade",
                min_value=-1,
                max_value=10,
                value=profundidade_notion_atual
            )
            numero_paginas = st.number_input(
                "Número de páginas",
                min_value=-1,
                max_value=100,
                value=numero_paginas_notion_atual
            )

            api_notion_key = st.text_input(
                "Token da API do Notion",
                key="ti_notion_api_token",
                type="password",
                value=default_api_key
            )

            indexar_notion = st.button("Atualizar Configurações Notion")

            if indexar_notion:
                st.session_state["notion_api_token"] = api_notion_key
                st.session_state["notion_profundidade"] = profundidade
                st.session_state["notion_numero_paginas"] = numero_paginas
    return None, None

def notion_search_and_select(user_input_message):
    if "notion_uploader_counter" not in st.session_state:
        st.session_state["notion_uploader_counter"] = 0

    old_notion_counter = st.session_state["notion_uploader_counter"]

    with st.container():
        with st.form(key="notion_search_form", clear_on_submit=True, border=False):
            col1, col2 = st.columns([2, 1])

            # Input URL and Button
            with col1:
                notion_url = st.text_input(
                    "Sua URL do Notion",
                    key="notion_url",
                    label_visibility='collapsed',
                    placeholder='Notion URL',
                    autocomplete="off"
                )
            with col2:
                buscar_notion = st.form_submit_button("Buscar", use_container_width=True)

        col1, col2 = st.columns([2, 1])

        # Multiselect
        notion_nodes = st.session_state.get("notion_nodes", {})

        profundidade = str(st.session_state.get("notion_profundidade", 1))
        numero_paginas = st.session_state.get("notion_numero_paginas", -1)

        with col1:
            notion_container = st.empty()
        
            def create_multiselect(notion_multiselect_id):
                return notion_container.multiselect(
                    "Urls do notion indexadas",
                    options=list(notion_nodes.items()),
                    default=list(notion_nodes.items()),
                    key="selected_node_urls_" + str(notion_multiselect_id),
                    label_visibility='collapsed',
                    format_func=lambda x: x[1].object + ": " + x[0],
                )
            selected_nodes = create_multiselect(old_notion_counter)

        with col2:
            file_data = ""
            file_name = ""
            mime = "text/plain"

            if len(selected_nodes) > 1:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, mode="a", compression=zipfile.ZIP_STORED, allowZip64=True) as zip_file:
                    for url, node in selected_nodes:
                        # conver the url to a valid file name
                        file_url = url.replace("/", "_").replace(":", "_").replace(".", "_")

                        if isinstance(node, DatabaseNode):
                            zip_file.writestr(f"{file_url}.csv", node.to_dataframe().to_csv().encode('utf-8'))
                        else:
                            zip_file.writestr(f"{file_url}.md", node.to_markdown())

                zip_buffer.seek(0)

                mime = "application/zip"
                file_data = zip_buffer.getvalue()
                file_name = f"notion_nodes_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
            elif len(selected_nodes) == 1:
                url = selected_nodes[0][0]
                node = selected_nodes[0][1]

                if isinstance(node, DatabaseNode):
                    file_data = node.to_dataframe().to_csv().encode('utf-8')
                    file_name = f"{url}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
                else:
                    file_data = node.to_markdown()
                    file_name = f"{url}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

            # download selected nodes
            st.download_button(
                label="Download",
                data=file_data,
                file_name=file_name,
                mime=mime,
                use_container_width=True,
            )

        if buscar_notion:
            if notion_url:
                # verify if notion_url is already in the notion_nodes. If so, toast a warning
                if notion_url in notion_nodes:
                    # TODO: verify the whole notion graph to check if the URL is already indexed
                    st.toast("🚨 Esta URL do Notion já foi indexada. 🚨")
                    return

                kwargs = {}
                if profundidade != -1:
                    kwargs["max_depth"] = int(profundidade)
                if numero_paginas != -1:
                    kwargs["page_size"] = int(numero_paginas)

                with st.status("Indexando Notion..."):
                    try:
                        api_notion_key = st.session_state["notion_api_token"]
                        notion_reader = NotionReader(integration_token=api_notion_key)
                        notion_node = notion_reader.load_data(
                            notion_url,
                            **kwargs
                        )
                        notion_nodes[notion_url] = notion_node

                        # Update the session state with the fetched nodes
                        st.session_state["notion_nodes"] = notion_nodes
                    except Exception as e:
                        st.toast("❌ Erro ao indexar o Notion. Verifique a URL e o token da API: " + str(e))
                        return

                # Update the multiselect options by rerun
                st.rerun()
            else:
                st.toast("⚠️ Por favor, insira uma URL do Notion. ⚠️")

    if user_input_message and len(user_input_message) > 0 and len(selected_nodes) > 0:
        # remove the selected_nodes from st.session_state["notion_nodes"]
        for url, _ in selected_nodes:
            del st.session_state["notion_nodes"][url]

        st.session_state["notion_uploader_counter"] += 1
        new_input_counter = st.session_state["notion_uploader_counter"]
        create_multiselect(new_input_counter)

    return selected_nodes

def main():
    maybe_st_initialize_state()
    chat_connector = create_chat_connector()

    notion_url, notion_node = setup_notion_indexing()

    model_settings()

    genai.configure(api_key=st.session_state["api_token_value"])

    with stylable_container(key="main_container", css_styles="""
            {
                left: 0;
                bottom: 10px;
                width: 100%;
                position: fixed;
                overflow-y: auto;
                max-height: 100vh;
                overflow-x: hidden;
                padding-left: 10vw;
                padding-right: 10vw;
                padding-bottom: 15px;
            }
    """):
        parent_chat_container = stylable_container(key="chat_container", css_styles="""
                {
                    min-height: 5vh;
                    height: calc(100% - 90px);
                    max-height: calc(93vh - 90px);
                }
        """)

        with stylable_container(
            key="footer_container",
            css_styles="""
                * {
                    max-height: 100px;
                }
                div[data-testid="stPopover"] {
                    min-width: 50px;
                    max-width: 7vw;
                }
                div[data-baseweb="popover"] > div {
                    min-width: 40vw;
                }
            """
        ):
            columns = st.columns([1, 1, 8])

            notion_popover = columns[0].popover("📝", use_container_width=True)

            files_popover = columns[1].popover("📎", use_container_width=True)

            with columns[2]:
                user_input_message = st.chat_input("Digite sua mensagem aqui...")

            with notion_popover:
                selected_nodes = notion_search_and_select(user_input_message)

            with files_popover:
                user_uploaded_files = file_uploader_fragment(user_input_message)

            if selected_nodes:
                transformed_notion_files = []
                for url, notion_node in selected_nodes:
                    if isinstance(notion_node, DatabaseNode):
                        transformed_notion_files.append(
                            PandasFile("NotionDatabase", notion_node.to_dataframe())
                        )
                    else:
                        transformed_notion_files.extend([TextFile("NotionContent", notion_node.to_markdown(), "md")])

                user_uploaded_files.extend(transformed_notion_files)

        with parent_chat_container:
            with st.container(height=10000, border=False):
                chat_messages(chat_connector, user_input_message, user_uploaded_files)

main()
