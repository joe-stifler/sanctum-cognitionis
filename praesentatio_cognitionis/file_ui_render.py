# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.files import (
    PandasFile, PDFFile, AudioFile, ImageFile, TextFile, JsonFile, CodeFile, VideoFile
)

# module imports from the standard python environment
import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from streamlit_extras.stylable_container import stylable_container

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
            with stylable_container(key="file_container", css_styles="""
                    {
                        max-height: 450px;
                    }
            """):
                if isinstance(file, ImageFile):
                    st.image(file.content, caption=file.name)
                elif isinstance(file, PDFFile):
                    all_counter = st.session_state.get('pdf_counter', 0)
                    pdf_viewer(file.content, height=450, key=f"pdf_{all_counter}_{idx}")
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
