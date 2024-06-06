# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.logger import setup_logger
from praesentatio_cognitionis.chat_connector import create_chat_connector
from praesentatio_cognitionis.model_settings import model_settings
from praesentatio_cognitionis.chat_render import render_chat_history, chat_messages
from praesentatio_cognitionis.file_uploader import file_uploader_fragment
from praesentatio_cognitionis.notion_ui_render import notion_search_and_select
from praesentatio_cognitionis.header import show_header

show_header(0)

# module imports from the standard python environment
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

logger = setup_logger()


################################################################################
def main():
    if "start_new_conversation" not in st.session_state:
        st.session_state["start_new_conversation"] = False

    chat_connector = create_chat_connector()

    # Get the URL query params
    notion_token = st.query_params.get("notion_token")
    google_token = st.query_params.get("google_token")
    persona_name = st.query_params.get("persona_name")
    model_name = st.query_params.get("model_name")
    notion_url = st.query_params.get("notion_url")
    notion_depth = st.query_params.get("notion_depth")

    with stylable_container(
        key="main_container",
        css_styles="""
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
                padding-bottom: 25px;
            }
    """,
    ):
        parent_chat_container = stylable_container(
            key="chat_container",
            css_styles="""
                {
                    margin-top: 60px;
                    height: calc(100% - 90px);
                    max-height: calc(93vh - 90px);
                }
        """,
        )

        with stylable_container(
            key="footer_container",
            css_styles="""
                * {
                    max-height: 200px;
                }
                div[data-testid="stPopover"] {
                    min-width: 50px;
                    max-width: 7vw;
                }
                div[data-baseweb="popover"] {
                    min-width: 35vw;
                }
            """,
        ):
            columns = st.columns([1, 1, 8])
            notion_popover = columns[0].popover("📝", use_container_width=True)
            files_popover = columns[1].popover("📎", use_container_width=True)

            with columns[2]:
                user_input_message = st.chat_input("Type your message here...")

            with notion_popover:
                selected_nodes = notion_search_and_select(
                    user_input_message, notion_url, notion_depth, notion_token
                )

            with files_popover:
                user_uploaded_files = file_uploader_fragment(user_input_message)

            user_uploaded_files.extend(selected_nodes)

        with parent_chat_container:
            api_status = model_settings(
                chat_connector, logger, google_token, persona_name, model_name
            )

            with st.container(height=10000, border=False):
                if api_status:
                    chat_history = render_chat_history(chat_connector, logger)
                    chat_messages(
                        chat_history, user_input_message, user_uploaded_files, logger
                    )
                else:
                    warning_message = "⚠️ Set your Google API Key above. Follow the instructions in the [official website](https://makersuite.google.com/app/apikey) to create a new API Key."
                    st.warning(warning_message)


main()
