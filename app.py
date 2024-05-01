# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.header import show_header
show_header(0)

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.mock import LLMMockFamily
from servitium_cognitionis.llms.gemini import LLMGeminiFamily

# module imports from the standard python environment
import os
import hmac
import time
import uuid
import vertexai
import google.auth
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_extras.stylable_container import stylable_container
from praesentatio_cognitionis.fixed_container import st_fixed_container

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

def barfi_demo():
    from barfi import barfi_schemas, Block, st_barfi

    feed = Block(name='Feed')
    feed.add_output()
    def feed_func(self):
        self.set_interface(name='Output 1', value=4)
    feed.add_compute(feed_func)

    splitter = Block(name='Splitter')
    splitter.add_input()
    splitter.add_output()
    splitter.add_output()
    def splitter_func(self):
        in_1 = self.get_interface(name='Input 1')
        value = (in_1/2)
        self.set_interface(name='Output 1', value=value)
        self.set_interface(name='Output 2', value=value)
    splitter.add_compute(splitter_func)

    mixer = Block(name='Mixer')
    mixer.add_input()
    mixer.add_input()
    mixer.add_output()
    def mixer_func(self):
        in_1 = self.get_interface(name='Input 1')
        in_2 = self.get_interface(name='Input 2')
        value = (in_1 + in_2)
        self.set_interface(name='Output 1', value=value)
    mixer.add_compute(mixer_func)

    result = Block(name='Result')
    result.add_input()
    def result_func(self):
        in_1 = self.get_interface(name='Input 1')
    result.add_compute(result_func)

    load_schema = st.selectbox('Select a saved schema:', barfi_schemas())

    compute_engine = st.checkbox('Activate barfi compute engine', value=False)

    barfi_result = st_barfi(base_blocks=[feed, result, mixer, splitter],
                        compute_engine=compute_engine, load_schema=load_schema)

    if barfi_result:
        st.write(barfi_result)



################################################################################

def maybe_st_initialize_state(use_dummy_llm=False):
    if "llm_families" not in st.session_state:
        llm_families = [
            LLMMockFamily(),
            LLMGeminiFamily()
        ]

        st.session_state["llm_families"] = {
            llm_family_idx: llm_family for llm_family_idx, llm_family in enumerate(llm_families)
        }
        st.session_state["chosen_llm_family_idx"] = 0 if use_dummy_llm else 1

    if "persona_settings" not in st.session_state:
        default_persona_description_path = 'personas/professores/redacao/dani-stella/persona_dani_stella.md'

        with open(default_persona_description_path, 'r', encoding='utf-8') as file:
            default_persona_description = file.read()

        st.session_state["persona_settings"] = {
            "persona_name": "Dani Stella",
            "persona_files": [
                # "personas/professores/redacao/dani-stella/conectivos.md",
                # "personas/professores/redacao/dani-stella/operadores-argumentativos.md",
                # "personas/professores/redacao/dani-stella/generos-do-discurso.md",
                # "databases/redacao/unicamp/unicamp_redacoes_candidatos.json",
                # "databases/redacao/unicamp/unicamp_redacoes_propostas.json",
                # "personas/professores/redacao/dani-stella/a_redacao_na_unicamp.md",
                # "personas/professores/redacao/dani-stella/informacoes_importantes_sobre_a_redacao_unicamp.md",
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

    os.environ["LANGCHAIN_TRACING_V2"] = str(st.secrets["LANGCHAIN"]["LANGCHAIN_TRACING_V2"])
    os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN"]["LANGCHAIN_ENDPOINT"]
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN"]["LANGCHAIN_API_KEY"]
    os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN"]["LANGCHAIN_PROJECT"]

    gemini_cloud_location = st.secrets["VERTEXAI"]["GEMINI_CLOUD_LOCATION"]
    _, project_id = google.auth.default()
    vertexai.init(project=project_id, location=gemini_cloud_location)


def convert_files_to_str(files_path: str):
    files_content = "## Arquivos disponíveis na base de conhecimento do professor(a):\n\n"
    files_content += "--------------------------------------------------------\n\n"

    for file_path in files_path:
        files_content += f"### Conteúdo do arquivo `{file_path}`:\n\n"

        extension = file_path.split(".")[-1]
        with open(file_path, "r", encoding='utf-8') as file:
            files_content += f"```{extension}\n" + file.read() + "\n```\n\n"

    return files_content


def get_ai_chat():
    llm_family = st.session_state["llm_families"][st.session_state["chosen_llm_family_idx"]]
    persona_name = st.session_state["persona_settings"]["persona_name"]
    persona_name=f':red[{persona_name}]'

    persona_description = st.session_state["persona_settings"]["persona_description"]

    persona_files = st.session_state["persona_settings"]["persona_files"]
    persona_files_str = convert_files_to_str(persona_files)
    prompt_with_files_str = f"{persona_files_str}\n\n---\n\n{persona_description}"

    ai_base_prompt = prompt_with_files_str

    return llm_family, ai_base_prompt

class ChatHistory:
    def __init__(self, session_id, llm_family, ai_base_prompt):
        self.chat_messages = []
        self.user_avatar = "👩🏾‍🎓"
        self.ai_avatar = "👩🏽‍🏫"
        self.ai_name = ":orange[IA]"
        self.llm_family = llm_family
        self.session_id = session_id
        self.user_name = ":blue[estudante]"
        self.ai_base_prompt = ai_base_prompt
        self.ai_model = None

    def initialize_chat(self):
        self.ai_model = self.llm_family.current_model()
        self.ai_model.initialize_model()
        self.ai_model.create_chat(self.session_id)
        return self.send_ai_message(self.ai_base_prompt)

    def add_new_ai_message(self, ai_message, **kwargs):
        print("Adding new AI message:", ai_message)
        print("With kwargs:", kwargs, "\n\n")
        self.chat_messages.append(AIMessage(ai_message, **kwargs))

    def send_ai_message(self, user_message):
        user_message = f"mensagem do usuário: {user_message}"
        ai_response_stream = self.ai_model.send_stream_chat_message(self.session_id, user_message)

        for text_message, ai_message_args in ai_response_stream:
            self.add_new_ai_message(text_message, **ai_message_args)
            yield text_message

    def send_user_message(self, user_message):
        self.chat_messages.append(HumanMessage(user_message))
        return self.send_ai_message(user_message)

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
                messages.append(("assistant", self.ai_avatar, message_content))
        return messages


class ChatConnector:
    def __init__(self):
        self.chats = {}

    def create_chat_history(self):
        session_id = str(uuid.uuid4().hex)
        print("Length of chats", len(self.chats))
        print("Creating chat history with session_id", session_id)
        st.session_state["session_id"] = session_id

        llm_family, ai_base_prompt = get_ai_chat()
        self.chats[session_id] = ChatHistory(session_id, llm_family, ai_base_prompt)

        return self.chats[session_id]

    def fetch_chat_history(self, session_id):
        if session_id not in self.chats:
            assert False, f"Chat with session_id {session_id} not found"
        return self.chats[session_id]


@st.cache_resource
def create_chat_connector():
    return ChatConnector()

@st.experimental_fragment
def chat_messages(chat_connector, user_input_message):
    if "session_id" not in st.session_state:
        chat_history = chat_connector.create_chat_history()
    else:
        chat_history = chat_connector.fetch_chat_history(st.session_state["session_id"])

    # Display chat history messages
    for role, avatar, message in chat_history.get_chat_messages():
        with st.chat_message(role, avatar=avatar):
            st.markdown(message)

    if len(chat_history.get_chat_messages()) == 0:
        with st.spinner("Inicializando o modelo..."):
            ai_response = chat_history.initialize_chat()
            with st.chat_message("assistant", avatar="👩🏽‍🏫"):
                st.write_stream(ai_response)

    # Display user message
    with st.chat_message("user", avatar="👩🏾‍🎓"):
        st.write(user_input_message)

    # Send user message to AI inference
    ai_response = chat_history.send_user_message(user_input_message)

    # Display AI response
    with st.spinner("Processando resposta..."):
        with st.chat_message("assistant", avatar="👩🏽‍🏫"):
            st.write_stream(ai_response)

@st.experimental_fragment
def file_uploader():
    with stylable_container(
        key="file_uploader_container",
        css_styles="""
            section[data-testid='stFileUploaderDropzone']:active {
                width: 100%;
                pointer-events: none;
            }
            section[data-testid='stFileUploaderDropzone']:hover {
                width: 100%;
                cursor: grab;
                opacity: 0.2;
                content: "Arraste um arquivo aqui";
            }
            section[data-testid='stFileUploaderDropzone'] {
                cursor: unset;
                height: 2.5rem;
                opacity: 0;
            }
            div[data-testid='stFileUploaderDropzoneInstructions'] {
                visibility: hidden;
            }
            button[data-testid='baseButton-secondary'] {
                visibility: hidden;
            }
        """,
    ):
        st.file_uploader("Upload de arquivos", accept_multiple_files=True, label_visibility="collapsed")

def main():
    maybe_st_initialize_state(use_dummy_llm=False)

    chat_connector = create_chat_connector()

    with st_fixed_container(id="file_uploader", mode="fixed", position="bottom", border=False, margin="6.2rem"):
        file_uploader()

    user_input_message = st.chat_input("Digite sua mensagem ou arraste arquivos acima")

    with st_fixed_container(mode="fixed", position="top", border=False, margin="2.9rem"):
            config = st.expander("Configurações do chat", expanded=False)
            width = 50
            width = max(width, 0.01)
            side = max((100 - width) / 2, 0.01)
            
            with config:
                _, container, _ = st.columns([side, width, side])
                
                with container:
                    # embed streamlit docs in a streamlit app
                    st.video("https://www.youtube.com/watch?v=Gcm-tOGiva0")

    if user_input_message:
        with stylable_container(
            key="chat_container2",
            css_styles="""
                {   
                    margin-top: 5px;
                    margin-bottom: 40px;
                }
                """,
        ):
            chat_messages(chat_connector, user_input_message)

main()
