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
import google.auth
import pandas as pd
import streamlit as st
from pathlib import Path
from tempfile import NamedTemporaryFile
from streamlit_pdf_viewer import pdf_viewer
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
        log_name = f"{log_dir}/app_{creation_date}_{log_id}.log"
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


class ChatHistory:
    def __init__(self, session_id, llm_model, persona):
        self.persona = persona
        self.chat_messages = []
        self.user_avatar = "👩🏾‍🎓"
        self.llm_model = llm_model
        self.session_id = session_id
        self.chat_num_lines = 0

    def add_new_ai_message(self, ai_message, **kwargs):
        logger.debug("Adding new AI message: %s", ai_message)
        logger.debug("With kwargs: %s", kwargs)
        logger.debug("\n\n")
        self.chat_messages.append(AIMessage(ai_message, extra_args=kwargs))

    def initialize_chat(self, user_message, user_uploaded_files=[]):
        self.llm_model.initialize_model(
            temperature=self.persona.creativity_level,
            max_output_tokens=self.persona.speech_conciseness,
        )
        self.llm_model.create_chat(self.session_id)

        persona_presentation = self.persona.present_yourself()

        initial_ai_description_with_user_message = (
            persona_presentation +
            "\n\n---\n\n" +
            "# Acima estão as informações iniciais sobre quem e como você deve se comportar.\n" +
            "# Agora abaixo está a primeira mensagem do usuário que você deve responder: \n\n" +
             user_message
        )
        return self.send_ai_message(
            initial_ai_description_with_user_message,
            user_uploaded_files=user_uploaded_files
        )

    def send_ai_message(self, user_message, user_uploaded_files={}):
        user_message = f"# Mensagem do usuário:\n\n{user_message}"
        ai_response_stream = self.llm_model.send_stream_chat_message(
            self.session_id,
            user_message,
            user_uploaded_files
        )

        for text_message, ai_message_args in ai_response_stream:
            self.add_new_ai_message(text_message, **ai_message_args)
            self.chat_num_lines += text_message.count("\n")
            yield text_message

    def send_user_message(self, user_message, user_uploaded_files=[]):
        user_uploaded_files_ai = [(uploaded_file.name, uploaded_file.read()) for uploaded_file in user_uploaded_files]
        
        self.chat_num_lines += user_message.count("\n")
        self.chat_messages.append(HumanMessage(user_message, upload_files=user_uploaded_files))

        logger.info("Sending user message: %s", user_message)

        if len(self.get_chat_messages()) == 1:
            logger.info("Initializing chat")
            return self.initialize_chat(user_message, user_uploaded_files=user_uploaded_files_ai)

        return self.send_ai_message(user_message, user_uploaded_files=user_uploaded_files_ai)

    def get_chat_num_lines(self):
        return self.chat_num_lines

    def get_chat_messages(self):
        messages = []
        message_pos = 0

        while message_pos < len(self.chat_messages):
            message = self.chat_messages[message_pos]
            if isinstance(message, HumanMessage):
                messages.append(("user", self.user_avatar, message.content, message.upload_files))
                message_pos += 1
            else:
                message_content = ""
                message_args = []
                while message_pos < len(self.chat_messages) and not isinstance(self.chat_messages[message_pos], HumanMessage):
                    message_content += self.chat_messages[message_pos].content
                    extra_args = self.chat_messages[message_pos].extra_args
                    if len(extra_args) > 0:
                        message_args.append(extra_args)

                    message_pos += 1
                messages.append(("assistant", self.persona.avatar, message_content, message_args))
        return messages


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

def write_files(role, files):
    if len(files) == 0:
        return

    st.divider()
    st.write(f"**Arquivos associados:**")

    if role == "assistant":
        num_cols = min(3, len(files))
        with st.expander(f"**Metadados da resposta**", expanded=False):
            # cols = st.columns(num_cols)
            result = pd.json_normalize(files)
            print(result)
            st.dataframe(result)

            # for idx, arguments in enumerate(files):
            #     with cols[idx % num_cols]:
            #         st.divider()
            #         st.write(f"{idx}\. Argumentos:")
            #         st.json(arguments)

        return

    for idx, file in enumerate(files):
        with st.expander(f"**{idx}\. {file.name}:**", expanded=True):
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
                # file not supported
                st.error(f"Arquivo não suportado: {file.name}")

# @st.experimental_fragment
def chat_messages(chat_connector, user_input_message, user_uploaded_files):
    if "session_id" in st.session_state:
        chat_history = chat_connector.fetch_chat_history(st.session_state["session_id"])

        # Display chat history messages
        for role, avatar, message, args in chat_history.get_chat_messages():
            with st.chat_message(role, avatar=avatar):
                st.write(message)

                if len(args) > 0:
                    write_files(role, args)

    if user_input_message:
        try:
            user_uploaded_files = [uploaded_file for uploaded_file in user_uploaded_files]

            if "session_id" not in st.session_state:
                chat_history = chat_connector.create_chat_history()

            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(user_input_message)

                if len(user_uploaded_files) > 0:
                    write_files("user", user_uploaded_files)

            # Send user message to AI inference
            ai_response = chat_history.send_user_message(user_input_message, user_uploaded_files)

            # Display AI response
            with st.spinner("Processando resposta..."):
                with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                    st.write_stream(ai_response)
        except FileNotFoundError as e:
            logger.error("Erro ao inicializar a persona: %s", str(e))
            st.error(f"Erro ao inicializar a persona: {e}")
        except Exception as e:
            logger.error("Erro ao enviar mensagem: %s", str(e))
            st.error(f"Erro ao enviar mensagem: {e}")

    if "session_id" not in st.session_state:
        st.info("Dani Stella está pronta para conversar! Envie uma mensagem para começar.")

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

        col1, col2 = st.columns([1, 13], gap="small")

        with col1:
            with st.popover("Upload"):
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
