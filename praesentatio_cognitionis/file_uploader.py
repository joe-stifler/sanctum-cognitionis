# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.streamlit_file_handler import StreamlitFileHandler

# module imports from the standard python environment
import streamlit as st

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
