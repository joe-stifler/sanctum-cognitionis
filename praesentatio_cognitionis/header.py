import streamlit as st

def show_header(page_idx):
    pages = [
        {
            "title": "Sanctum Cognitionis",
            "icon": "🧠",
        },
    ]

    st.set_page_config(
        page_title=pages[page_idx]["title"],
        page_icon=pages[page_idx]["icon"],
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': """
- [LinkedIn](https://www.linkedin.com/in/-jose-ribeiro-)
- [GitHub](https://github.com/joe-stifler)

---
            """
        }
    )

    # columns = st.columns([1, 1, 1], gap="large")

    # for col, page in zip(columns, pages):
    #     with col:
    #         st.page_link(page["file"], label=page["title"], icon=page["icon"])

    # st.divider()
