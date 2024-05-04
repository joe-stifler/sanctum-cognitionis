# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_history import ChatHistory
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.mock import LLMMockFamily
from servitium_cognitionis.llms.gemini import LLMGeminiFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the standard python environment
import os
import hmac
import time
import uuid
import logging
import datetime
import vertexai
import traceback
import google.auth
import pandas as pd
import streamlit as st
from pathlib import Path
from streamlit_extras.row import row
from tempfile import NamedTemporaryFile
from streamlit_pdf_viewer import pdf_viewer
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

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


# if not check_password():
#     st.stop()

pc = st.get_option('theme.primaryColor')
bc = st.get_option('theme.backgroundColor')
sbc = st.get_option('theme.secondaryBackgroundColor')
tc = st.get_option('theme.textColor')

################################################################################

def maybe_st_initialize_state():
    if "persona_settings_path" not in st.session_state:
        st.session_state["persona_settings_path"] = "dados/personas/professores/redacao/dani-stella/persona_config.json"

        logger.info("Setting persona settings path to: %s", st.session_state["persona_settings_path"])

    key_path = ".streamlit/google_secrets.json"

    if "created_google_json" not in st.session_state:
        st.session_state["created_google_json"] = True

        if not os.path.exists(".streamlit"):
            os.makedirs(".streamlit")

        with open(key_path, "w", encoding='utf-8') as file:
            file.write(st.secrets["VERTEXAI"]["GOOGLE_JSON_SECRETS"])

        time.sleep(0.1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    os.environ["LANGCHAIN_TRACING_V2"] = str(st.secrets["LANGCHAIN"]["LANGCHAIN_TRACING_V2"])
    os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN"]["LANGCHAIN_ENDPOINT"]
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN"]["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN"]["LANGCHAIN_PROJECT"]

    gemini_cloud_location = st.secrets["VERTEXAI"]["GEMINI_CLOUD_LOCATION"]
    _, project_id = google.auth.default()
    vertexai.init(project=project_id, location=gemini_cloud_location)

    return create_chat_connector()


def get_ai_chat():
    persona_settings_path = st.session_state["persona_settings_path"]
    persona = Persona.from_json(persona_settings_path)

    llm_family = None

    if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
        llm_family = LLMMockFamily()
        logger.info("Using LLMMockFamily")
    elif persona.thinking_style == "LLMGeminiFamily":
        llm_family = LLMGeminiFamily()
        logger.info("Using LLMGeminiFamily")
    elif persona.thinking_style == "LLMMockFamily":
        llm_family = LLMMockFamily()
        logger.info("Using LLMMockFamily")

    llm_model = llm_family.get_model(persona.thought_process)

    return llm_model, persona


class ChatConnector:
    def __init__(self):
        self.chats = {}

    def create_chat_history(self):
        session_id = str(uuid.uuid4().hex)
        llm_model, persona = get_ai_chat()
        logger.info("Chosen Persona: %s", persona)
        logger.info("Chosen LLM Model: %s", llm_model)

        logger.info("Length of chats: %s", len(self.chats))
        logger.info("Creating chat history with session_id: %s", session_id)
        st.session_state["session_id"] = session_id
        self.chats[session_id] = ChatHistory(session_id, llm_model, persona)

        return self.chats[session_id]

    def fetch_chat_history(self, session_id):
        if session_id not in self.chats:
            assert False, f"Chat with session_id {session_id} not found"
        return self.chats[session_id]

@st.cache_resource
def create_chat_connector():
    logger.info("Creating chat connector")
    return ChatConnector()

def write_medatada_chat_message(role, files):
    if len(files) == 0:
        return

    st.divider()

    if role == "assistant":
        num_cols = min(3, len(files))
        with st.expander("**Metadados da resposta**", expanded=False):
            cols = st.columns(num_cols)

            for idx, arguments in enumerate(files):
                with cols[idx % num_cols]:
                    st.divider()
                    st.write(f"{idx}. Argumentos:")
                    st.json(arguments)

        return

    st.write("**Arquivos associados:**")

    for idx, file in enumerate(files):
        with st.expander(f"**{idx}. {file.name}:**", expanded=True):
            suffix = Path(file.name).suffix

            if suffix in [".png", ".jpg", ".jpeg", ".gif"]:
                st.image(file)
            elif suffix in [".csv"]:
                st.data_editor(pd.read_csv(file))
            elif suffix in [".xlsx", ".xls"]:
                st.data_editor(pd.read_excel(file))
            elif suffix in [".json"]:
                st.data_editor(pd.read_json(file), num_rows='dynamic')
            elif suffix in [".pdf"]:
                with NamedTemporaryFile(dir='.', suffix=suffix) as f:
                    f.write(file.getbuffer())
                    pdf_viewer(f.name, height=600, width=700)
            elif suffix in [".txt"]:
                st.text(file.read().decode('utf-8'))
            elif suffix in [".py"]:
                st.code(file.read().decode('utf-8'), language='python')
            elif suffix in [".md"]:
                st.markdown(file.read().decode('utf-8'))
            elif suffix in [".html"]:
                st.markdown(file.read().decode('utf-8'), unsafe_allow_html=True)
            elif suffix in [".cpp", '.c', '.h', '.hpp']:
                st.code(file.read().decode('utf-8'), language='cpp')
            else:
                st.error(f"Arquivo não suportado: {file.name}")

def chat_messages(chat_connector, user_input_message, user_uploaded_files):
    # Initialize or fetch existing chat history
    if "session_id" not in st.session_state:
        chat_history = chat_connector.create_chat_history()
        st.session_state["session_id"] = chat_history.session_id
        st.session_state["chat_history"] = chat_history
    else:
        chat_history = st.session_state["chat_history"]

    # Display past messages from chat history
    if chat_history:
        for chat_message in chat_history.chat_messages:
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(":blue[Usuário]")
                st.write(chat_message.user_message)
                write_medatada_chat_message("assistant", chat_message.user_uploaded_files)

            with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                st.write(f":red[{chat_message.ai_name}]")
                st.write(''.join(chat_message.ai_messages))

                if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
                    write_medatada_chat_message("assistant", chat_message.ai_extra_args)

    if user_input_message:
        try:
            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(f":blue[Usuário]")
                st.write(user_input_message)

            logger.debug("Sending user message:\n\n```text\n%s\n```", user_input_message)

            # Send user message to AI inference
            new_chat_message = chat_history.send_ai_message(
                user_input_message, user_uploaded_files
            )

            # Display AI responses
            with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                with st.spinner('Processando sua mensagem...'):
                    st.write(f":red[{chat_history.get_persona().name}]")
                    st.write_stream(new_chat_message.process_ai_messages())

                    logger.debug(f"AI new messages: \n\n{new_chat_message.ai_extra_args}")
                    logger.debug(f"\n\nAI new message kwargs: \n\n{new_chat_message.ai_extra_args}")

                    write_medatada_chat_message("assistant", new_chat_message.ai_extra_args)
        except FileNotFoundError as e:
            logger.error("Erro ao inicializar a persona: %s", str(e))
            st.error(f"Erro ao inicializar a persona: {e}")
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            error_details = traceback.format_exc()
            logger.error(f"Error processing user input: %s\nDetails: %s", error_message, error_details)
            st.error(f"Sorry, there was a problem processing your message: {error_message}. Please try again.")
    else:
        if len(chat_history.chat_messages) == 0:
            st.info("Dani Stella está pronta para conversar! Envie uma mensagem para começar.")

def main():
    chat_connector = maybe_st_initialize_state()

    if "counter" not in st.session_state:
        st.session_state["counter"] = 0

    with stylable_container(key="main_container", css_styles="""
            {
                bottom: 0;
                left: 0;
                width: 100%;
                max-height: 100vh;
                position: fixed;
                overflow-y: auto;
                overflow-x: hidden;
                padding-left: 50px;
                padding-right: 50px;
            }
    """):
        parent_chat_container = stylable_container(key="chat_container", css_styles="""
                {
                    min-height: 5vh;
                    max-height: 80vh;
                    padding-top: 5vh;
                    position: relative;
                }
        """)

        with stylable_container(
            key="chat_input_container",
            css_styles="""
                {
                    white-space: nowrap;
                    margin-bottom: 3vh;
                }
                div[data-testid="stPopover"] {
                    min-width: 2rem;
                }
            """
        ):
            rows = row([1, 20], gap="small")

            with rows.popover("📎", use_container_width=True):
                files_container = st.empty()
                user_uploaded_files = files_container.file_uploader(
                    "Upload de arquivos",
                    accept_multiple_files=True,
                    label_visibility="collapsed",
                    key=st.session_state["counter"]
                )

            user_input_message = rows.chat_input("Digite sua mensagem aqui...")

        with parent_chat_container:
            with st.container(height=10000, border=False):
                chat_messages(chat_connector, user_input_message, user_uploaded_files)

main()
