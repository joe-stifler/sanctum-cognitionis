# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_connector import ChatConnector
from praesentatio_cognitionis.streamlit_file_handler import StreamlitFileHandler
from praesentatio_cognitionis.files import (
    PandasFile, PDFFile, AudioFile, ImageFile, TextFile, JsonFile, CodeFile, VideoFile
)
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.gemini import GeminiDevFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the notion_indexer
from notion_indexer.page_node import PageNode
from notion_indexer.database_node import DatabaseNode
from notion_indexer.notion_reader import NotionReader

# module imports from the standard python environment
import os
import io
import time
import uuid
import json
import zipfile
import logging
import datetime
import traceback
import streamlit as st
import google.generativeai as genai
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
def get_ai_chat():
    llm_family = GeminiDevFamily()
    llm_model_default_name = "GeminiDevModelPro1_5"

    persona_file = "dados/personas/professores/redacao/dani-stella/persona_config.json"

    # load persona_file file content into a python dictionary
    with open(persona_file, 'r', encoding='utf-8') as file:
        persona_data = json.load(file)
        persona = Persona(**persona_data)

    llm_model = llm_family.get_model(llm_model_default_name)

    return llm_model, persona

@st.cache_resource
def create_chat_connector():
    logger.info("Creating chat connector")
    return ChatConnector()

@st.experimental_fragment
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
        with st.expander(f"**{file.name}**", expanded=False):
            with st.container(height=450, border=False):
                if isinstance(file, ImageFile):
                    st.image(file.content, caption=file.name)
                elif isinstance(file, PDFFile):
                    all_counter = st.session_state.get('pdf_counter', 0)
                    pdf_viewer(file.content, height=600, key=f"pdf_{all_counter}_{idx}")
                    st.session_state['pdf_counter'] = all_counter + 1
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

@st.experimental_fragment
def render_chat_history(chat_connector):
    # Initialize or fetch existing chat history
    if "session_id" not in st.session_state:
        llm_model, persona = get_ai_chat()
        logger.info("Chosen Persona: %s", persona)
        logger.info("Chosen LLM Model: %s", llm_model)
        logger.info("Persona presenting yourself:\n\n%s", persona.present_yourself())
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

    # Display past messages from chat history
    if chat_history:
        for chat_message in chat_history.chat_messages:
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(":blue[Usuário]")
                st.write(chat_message.user_message)
                write_medatada_chat_message("user", chat_message.user_uploaded_files)

            with st.chat_message("assistant", avatar="👩🏻‍🏫"):
                st.write(f":red[{chat_message.ai_name}]")
                st.write(''.join(chat_message.ai_messages))

                # if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
                write_medatada_chat_message("assistant", chat_message.ai_extra_args)
    return chat_history

# @st.experimental_fragment
def chat_messages(chat_history, user_input_message, user_uploaded_files):
    if user_input_message:
        try:
            warning_message = "⚠️ Defina sua chave de API na barra lateral esquerda antes de iniciar a conversa."

            if not st.session_state["api_token_value"]:
                st.warning(warning_message)
                return

            st.session_state["start_new_conversation"] = True

            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(f":blue[Usuário]")
                st.write(user_input_message)
                logger.debug("user input: %s", user_input_message)
                with st.spinner("Processsando arquivos do usuário..."):
                    write_medatada_chat_message("usuario", user_uploaded_files)

            logger.debug("Sending user message:\n\n```text\n%s\n```", user_input_message)

            # Display AI responses
            with st.chat_message("assistant", avatar="👩🏻‍🏫"):
                st.write(f":red[{chat_history.get_persona().name}]")
                new_ai_message = st.empty()
                with st.spinner("Estou processando sua mensagem..."):
                    new_chat_message = chat_history.send_ai_message(
                        user_input_message, user_uploaded_files
                    )
                    new_ai_message.write_stream(new_chat_message.process_ai_messages())
                    logger.debug(f"AI new messages: \n\n{new_chat_message.ai_messages}")
                    logger.debug(f"\n\nAI new message kwargs: \n\n{new_chat_message.ai_extra_args}")

            st.session_state["start_new_conversation"] = False

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

    if len(chat_history.chat_messages) == 0:
        persona = chat_history.get_persona()
        st.info(f"""{persona.name} está pronta para falar contigo!\n\n""")

def file_uploader_fragment(user_input_message):
    if "file_uploader_counter" not in st.session_state:
        st.session_state["file_uploader_counter"] = 0

    old_input_counter = st.session_state["file_uploader_counter"]
    files_container = st.empty()

    @st.experimental_fragment
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
            st.session_state["api_token_value"] = st.secrets["GOOGLE_DEV"]["GOOGLE_API_KEY"]

    with st.sidebar:
        default_api_key = st.session_state["api_token_value"]

        with st.container():
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

            if "session_id" in st.session_state:
                del st.session_state["session_id"]

            st.rerun()

def setup_notion_indexing():
    with st.sidebar:
        if "notion_api_token" not in st.session_state:
            st.session_state["notion_api_token"] = None

            if "NOTION" in st.secrets:
                st.session_state["notion_api_token"] = st.secrets["NOTION"]["NOTION_API_KEY"]

        default_api_key = st.session_state["notion_api_token"]

        api_notion_key = st.text_input(
            "Token da API do Notion",
            key="ti_notion_api_token",
            type="password",
            value=default_api_key
        )

        indexar_notion = st.button("Atualizar Configurações Notion")

        if indexar_notion:
            st.session_state["notion_api_token"] = api_notion_key

@st.experimental_fragment
def notion_search_and_select(user_input_message):
    if "notion_uploader_counter" not in st.session_state:
        st.session_state["notion_uploader_counter"] = 0

    old_notion_counter = st.session_state["notion_uploader_counter"]

    with st.container():
        with st.form(key="notion_search_form", clear_on_submit=True, border=False):
            notion_url = st.text_input(
                "URL do Notion",
                key="notion_url",
                placeholder='Notion URL',
                autocomplete="off",
                help="Copie e cole a URL do Notion aqui."
            )

            if "profundidade_notion" not in st.session_state:
                st.session_state["profundidade_notion"] = 1

            profundidade_notion_atual = st.session_state["profundidade_notion"]

            profundidade = st.number_input(
                "Profundidade",
                min_value=-1,
                max_value=10,
                value=profundidade_notion_atual,
                placeholder="Profundidade da busca no Notion. -1 para buscar até o fim.",
                help="Profundidade da busca no Notion. -1 para buscar até o fim.",
            )

            # Input URL and Button
            buscar_notion = st.form_submit_button("Buscar", use_container_width=True)

        notion_nodes = st.session_state.get("notion_nodes", {})

        notion_container = st.empty()

        def create_multiselect(notion_multiselect_id):
            return notion_container.multiselect(
                "Urls do notion indexadas:",
                options=list(notion_nodes.items()),
                default=list(notion_nodes.items()),
                disabled=True,
                key="selected_node_urls_" + str(notion_multiselect_id),
                format_func=lambda x: x[1].object + ": " + x[0],
            )
        selected_nodes = create_multiselect(old_notion_counter)

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
                st.session_state["profundidade_notion"] = profundidade

                # verify if notion_url is already in the notion_nodes. If so, toast a warning
                if notion_url in notion_nodes:
                    # TODO: verify the whole notion graph to check if the URL is already indexed
                    st.toast("🚨 Esta URL do Notion já foi indexada. 🚨")
                    return

                kwargs = {}
                if profundidade != -1:
                    kwargs["max_depth"] = int(profundidade)

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

                        st.toast(f"🎉 Sucesso ao indexar a URL do Notion `{notion_url}`")

                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.toast("❌ Erro ao indexar o Notion. Verifique a URL e o token da API: " + str(e))
                        return

            else:
                st.toast("⚠️ Por favor, insira uma URL do Notion. ⚠️")

    if user_input_message and len(user_input_message) > 0 and len(selected_nodes) > 0:
        # remove the selected_nodes from st.session_state["notion_nodes"]
        for url, _ in selected_nodes:
            del st.session_state["notion_nodes"][url]

        st.session_state["notion_uploader_counter"] += 1
        new_input_counter = st.session_state["notion_uploader_counter"]
        create_multiselect(new_input_counter)

    if selected_nodes:
        transformed_notion_files = []

        for url, notion_node in selected_nodes:
            if isinstance(notion_node, DatabaseNode):
                transformed_notion_files.append(
                    PandasFile(f"Notion Database: {url}", notion_node.to_dataframe())
                )
            elif isinstance(notion_node, PageNode):
                content = notion_node.to_markdown().encode("utf-8")
                transformed_notion_files.extend([TextFile(f"Notion Page: {url}", notion_node.to_markdown(), "md")])
            else:
                content = notion_node.to_markdown().encode("utf-8")
                transformed_notion_files.extend([TextFile(f"Notion Block: {url}", content, "md")])

        return transformed_notion_files

    return []

def main():
    chat_connector = create_chat_connector()

    if "start_new_conversation" not in st.session_state:
        st.session_state["start_new_conversation"] = False

    setup_notion_indexing()

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
                div[data-baseweb="popover"] {
                    min-width: 35vw;
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

            user_uploaded_files.extend(selected_nodes)

        with parent_chat_container:
            with st.container(height=10000, border=False):
                chat_history = render_chat_history(chat_connector)
                chat_messages(chat_history, user_input_message, user_uploaded_files)

main()
