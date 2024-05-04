# module imports from the praesentatio_cognitionis package
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
from tempfile import NamedTemporaryFile
from streamlit_pdf_viewer import pdf_viewer
from streamlit_feedback import streamlit_feedback
from langchain_core.messages import HumanMessage, AIMessage
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
    if "persona_settings" not in st.session_state:
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


class ChatMessage:
    def __init__(self, message_id, ai_name, user_name, user_message, user_upload_files=None):
        self._ai_messages = []
        self.ai_name = ai_name
        self.user_name = user_name
        self._feedback_value = None
        self._message_id = message_id
        self._ai_messages_stream = None
        self._user_message = user_message
        self._timestamp = datetime.datetime.now()
        self._user_uploaded_files = user_upload_files

    @property
    def message_id(self):
        return self._message_id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def feedback_value(self):
        return self._feedback_value

    @feedback_value.setter
    def feedback_value(self, value):
        self._feedback_value = value

    @property
    def user_message(self):
        return self._user_message

    @property
    def user_uploaded_files(self):
        return self._user_uploaded_files

    @property
    def ai_messages(self):
        return [ai_message for ai_message, _ in self._ai_messages]

    @property
    def ai_extra_args(self):
        return [args for _, args in self._ai_messages]

    def add_ai_message(self, ai_message, **kwargs):
        self._ai_messages.append((ai_message, kwargs))

    def set_ai_message_stream(self, ai_message_stream):
        self._ai_messages_stream = ai_message_stream

    def process_ai_messages(self):
        if self._ai_messages_stream:
            for ai_message_chunk, ai_message_args_chunk in self._ai_messages_stream:
                logger.debug(f"Adding new AI message: {ai_message_chunk}")
                logger.debug(f"With kwargs: {ai_message_args_chunk}")
                self.add_ai_message(ai_message_chunk, **ai_message_args_chunk)
                yield ai_message_chunk


class ChatHistory:
    def __init__(self, session_id, llm_model, persona):
        self.persona = persona
        self.chat_messages = []
        self.llm_model = llm_model
        self.session_id = session_id

    def get_persona(self):
        return self.persona

    def maybe_initialize_chat_message(self):
        """Initialize the chat and return the system message."""
        if not self.llm_model.check_chat_session_exists(self.session_id):
            logger.info("Initializing chat")
            self.llm_model.initialize_model(
                temperature=self.persona.creativity_level,
                system_instruction=[
                    self.persona.present_yourself()
                ],
                max_output_tokens=self.persona.speech_conciseness
            )
            self.llm_model.create_chat(self.session_id)

    def create_new_message(self, user_message="", user_uploaded_files=None):
        """Create a new chat message and return it."""
        new_chat_message = ChatMessage(
            message_id=str(uuid.uuid4().hex),
            ai_name=self.persona.name,
            user_name="Usuário",
            user_message=user_message,
            user_upload_files=user_uploaded_files
        )
        self.chat_messages.append(new_chat_message)
        return new_chat_message

    def send_ai_message(self, user_message, user_uploaded_files=None):
        """Send AI response for a given chat message."""
        logger.info("Sending user message:\n\n```text\n%s\n```", user_message)
        self.maybe_initialize_chat_message()

        new_message = self.create_new_message(user_message, user_uploaded_files)
        ai_response_stream = self.llm_model.send_stream_chat_message(
            self.session_id,
            user_message,
            user_uploaded_files
        )
        new_message.set_ai_message_stream(ai_response_stream)

        return new_message


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


@st.experimental_fragment
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

            with st.chat_message("user", avatar="👩🏽‍🏫"):
                st.write(f":red[{chat_message.ai_name}]")
                st.write(''.join(chat_message.ai_messages))

                if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
                    write_medatada_chat_message("assistant", chat_message.ai_extra_args)

        if len(chat_history.chat_messages) == 0:
            st.info("Dani Stella está pronta para conversar! Envie uma mensagem para começar.")

    if user_input_message:
        try:
            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(f":blue[Usuário]")
                st.write(user_input_message)

            # Send user message to AI inference
            new_chat_message = chat_history.send_ai_message(
                user_input_message, user_uploaded_files
            )

            # Display AI responses
            with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                st.write(f":red[{chat_history.get_persona().name}]")
                with st.spinner('Processando sua mensagem...'):
                    st.write_stream(new_chat_message.process_ai_messages())
                write_medatada_chat_message("assistant", new_chat_message.ai_extra_args)
        except FileNotFoundError as e:
            logger.error("Erro ao inicializar a persona: %s", str(e))
            st.error(f"Erro ao inicializar a persona: {e}")
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            error_details = traceback.format_exc()
            logger.error(f"Error processing user input: %s\nDetails: %s", error_message, error_details)
            st.error(f"Sorry, there was a problem processing your message: {error_message}. Please try again.")


def main():
    maybe_st_initialize_state()
    chat_connector = create_chat_connector()

    with stylable_container(
        key="main_container",
        css_styles=f"""{{
            bottom: 0rem;
            z-index: 999999;
            position: fixed;
            padding-bottom: 2rem;
            background-color: {bc};
        }}
        """
    ):
        if "counter" not in st.session_state:
            st.session_state["counter"] = 0

        col1, col2 = st.columns([1, 40], gap="large")

        with col1:
            with st.popover("📎"):
                files_container = st.empty()
                user_uploaded_files = files_container.file_uploader("Upload de arquivos", accept_multiple_files=True, label_visibility="collapsed", key=st.session_state["counter"])

        with col2:
            user_input_message = st.chat_input("Digite sua mensagem aqui")

        if user_input_message:
            st.session_state["counter"] += 1
            files_container.file_uploader("Upload de arquivos", accept_multiple_files=True, label_visibility="collapsed", key=st.session_state["counter"])

    with st.container(height=700, border=False):
        chat_messages(chat_connector, user_input_message, user_uploaded_files)

main()
