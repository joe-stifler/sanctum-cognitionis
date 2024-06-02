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
    persona = chat_history.get_persona()

    # Display past messages from chat history
    for chat_message in chat_history.chat_messages:
        with st.chat_message("user", avatar="👩🏾‍🎓"):
            st.write(":blue[User]")
            st.write(chat_message.user_message)
            write_medatada_chat_message("user", chat_message.user_uploaded_files)

        with st.chat_message("assistant", avatar=persona.avatar):
            st.write(f":red[{chat_message.ai_name}]")
            st.write(''.join(chat_message.ai_messages))

            # if os.environ.get("FORCE_LLM_MOCK_FAMILY"):
            write_medatada_chat_message("assistant", chat_message.ai_extra_args)

    return chat_history

def chat_messages(chat_history, user_input_message, user_uploaded_files, logger):
    persona = chat_history.get_persona()

    if user_input_message:
        try:
            st.session_state["start_new_conversation"] = True

            # Display User Message
            with st.chat_message("user", avatar="👩🏾‍🎓"):
                st.write(":blue[User]")
                st.write(user_input_message)
                with st.spinner("Processing user files..."):
                    write_medatada_chat_message("user", user_uploaded_files)

            # Display AI responses
            with st.chat_message("assistant", avatar=persona.avatar):
                with st.spinner("I am processing your message..."):
                    st.write(f":red[{chat_history.get_persona().name}]")
                    new_ai_message = st.empty()
                    new_chat_message = chat_history.send_ai_message(
                        user_input_message, user_uploaded_files
                    )
                    new_ai_message.write_stream(new_chat_message.process_ai_messages())
                    logger.debug(f"\n\nAI new message kwargs: \n\n{new_chat_message.ai_extra_args}")

            st.session_state["start_new_conversation"] = False

        except FileNotFoundError as e:
            logger.error("Error during the persona initialization: %s", str(e))
            st.error(f"Error during the persona initialization: {e}")
        except Exception as e:
            error_str = str(e)

            error_details = traceback.format_exc()
            logger.error(f"Error processing user input: %s\nDetails: %s", error_str, error_details)

            if "400 API key not valid" in error_str:
                st.error("Error during chat initialization: invalid Google API key")
            else:
                st.error(f"Erro: {error_str}\nDetails: {error_details}")

    if len(chat_history.chat_messages) == 0:
        st.info(f"""`{persona.name}` is waiting to help you. Don't be shy! Take the initiave and ask for a critic.\n\n""")
