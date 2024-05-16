# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.file_ui_render import write_medatada_chat_message
from praesentatio_cognitionis.streamlit_file_handler import StreamlitFileHandler

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.gemini import GeminiDevFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the standard python environment
import traceback
import streamlit as st


@st.experimental_fragment
def render_chat_history(chat_connector, logger):
    chat_history = chat_connector.fetch_chat_history(st.session_state["session_id"])

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
def chat_messages(chat_history, user_input_message, user_uploaded_files, logger):
    if user_input_message:
        try:
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
