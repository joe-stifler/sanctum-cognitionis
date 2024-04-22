import streamlit as st

def show_header(page_idx):
    pages = [
        {
            "title": "Redacoes",
            "icon": "📚",
            "file": "pages/redacoes.py",
        },
    ]

    st.set_page_config(
        page_title=pages[page_idx]["title"],
        page_icon=pages[page_idx]["icon"],
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # columns = st.columns([1, 1, 1], gap="large")

    # for col, page in zip(columns, pages):
    #     with col:
    #         st.page_link(page["file"], label=page["title"], icon=page["icon"])

    # st.divider()
