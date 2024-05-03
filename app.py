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
import vertexai
import google.auth
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from langchain_core.messages import HumanMessage, AIMessage

def setup_logger():
    # Create a custom logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the minimum level of messages to log

    # Create handlers for stdout and file
    c_handler = logging.StreamHandler()  # Console handler
    f_handler = logging.FileHandler('app.log', mode='a')  # File handler
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

    def initialize_chat(self):
        self.llm_model.initialize_model(
            temperature=self.persona.creativity_level,
            max_output_tokens=self.persona.speech_conciseness,
        )
        self.llm_model.create_chat(self.session_id)
        persona_initial_state = self.persona.present_initial_state()
        return self.send_ai_message(persona_initial_state)

    def add_new_ai_message(self, ai_message, **kwargs):
        logger.debug("Adding new AI message: %s", ai_message)
        logger.debug("With kwargs: %s", kwargs)
        logger.debug("\n\n")
        self.chat_messages.append(AIMessage(ai_message, **kwargs))

    def send_ai_message(self, user_message, user_uploaded_files={}):
        logger.debug("Sending user message to ai: %s", user_message)
        user_message = f"mensagem do usuário: {user_message}"
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
        self.chat_num_lines += user_message.count("\n")
        self.chat_messages.append(HumanMessage(user_message))
        return self.send_ai_message(user_message, user_uploaded_files=user_uploaded_files)

    def get_chat_num_lines(self):
        return self.chat_num_lines

    def get_chat_messages(self):
        messages = []
        message_pos = 0

        while message_pos < len(self.chat_messages):
            message = self.chat_messages[message_pos]
            if isinstance(message, HumanMessage):
                messages.append(("user", self.user_avatar, message.content))
                message_pos += 1
            else:
                message_content = ""
                while message_pos < len(self.chat_messages) and not isinstance(self.chat_messages[message_pos], HumanMessage):
                    message_content += self.chat_messages[message_pos].content
                    message_pos += 1
                messages.append(("assistant", self.persona.avatar, message_content))
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

# @st.experimental_fragment
def chat_messages(chat_connector, user_input_message, user_uploaded_files):
    if "session_id" in st.session_state:
        chat_history = chat_connector.fetch_chat_history(st.session_state["session_id"])

        # Display chat history messages
        for role, avatar, message in chat_history.get_chat_messages():
            with st.chat_message(role, avatar=avatar):
                st.markdown(message)

    if user_input_message:
        if len(user_uploaded_files) > 0:
            print("User file list:", user_uploaded_files[0][0])

        if "session_id" not in st.session_state:
            chat_history = chat_connector.create_chat_history()

        if len(chat_history.get_chat_messages()) == 0:
            with st.spinner("Inicializando o modelo..."):
                ai_response = chat_history.initialize_chat()
                with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                    st.write_stream(ai_response)

        # Display user message
        with st.chat_message("user", avatar="👩🏾‍🎓"):
            st.write(user_input_message)

        # Send user message to AI inference
        ai_response = chat_history.send_user_message(user_input_message, user_uploaded_files)

        # Display AI response
        with st.spinner("Processando resposta..."):
            with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                st.write_stream(ai_response)

        st.write("")
        st.write("")
    else:
        st.info("Dani Stella está pronta para conversar! Envie uma mensagem para começar.")

def main():
    maybe_st_initialize_state()
    chat_connector = create_chat_connector()

        
    with stylable_container(
        key="main_container",
        css_styles="""{
            overflow-y: auto;
            position: fixed;
            bottom: 0rem;
            height: 100%;
            padding-top: 4rem;
        }
        """
    ):
        st.title("Dani Stella")
        st.divider()
        chat_history_container = st.container(height=700, border=True)

        with stylable_container(
            key="chat_input_container",
            css_styles="""{
                padding-bottom: 1rem;
            }
            """
        ):
            if "counter" not in st.session_state:
                st.session_state["counter"] = 0
            
            expander = st.expander("Upload de arquivos", expanded=False)
            with expander:
                files_container = st.empty()
                user_uploaded_files = files_container.file_uploader("Upload de arquivos", accept_multiple_files=True, label_visibility="collapsed", key=st.session_state["counter"])
                user_uploaded_files_list = [(uploaded_file.name, uploaded_file.read()) for uploaded_file in user_uploaded_files]

            user_input_message = st.chat_input("Digite sua mensagem aqui")

            if user_input_message:
                st.session_state["counter"] += 1
                files_container.file_uploader("Upload de arquivos", accept_multiple_files=True, label_visibility="collapsed", key=st.session_state["counter"])

        with chat_history_container:
            chat_messages(chat_connector, user_input_message, user_uploaded_files_list)

main()
