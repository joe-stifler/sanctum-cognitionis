# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.files import (
    PandasFile, TextFile
)

# module imports from the notion_indexer
from servitium_cognitionis.notion_indexer.page_node import PageNode
from servitium_cognitionis.notion_indexer.database_node import DatabaseNode
from servitium_cognitionis.notion_indexer.notion_reader import NotionReader

# module imports from the standard python environment
import io
import time
import zipfile
import datetime
import streamlit as st

@st.experimental_fragment
def notion_search_and_select(user_input_message):
    if "notion_uploader_counter" not in st.session_state:
        st.session_state["notion_uploader_counter"] = 0

    old_notion_counter = st.session_state["notion_uploader_counter"]

    with st.container():
        if "NOTION" in st.secrets:
            default_notion_api_key = st.secrets["NOTION"]["NOTION_API_KEY"]
            st.session_state["notion_api_token"] = default_notion_api_key

        notion_api_key = st.text_input(
            "Token do Notion",
            key="ti_notion_api_token",
            type="password",
            value=st.session_state.get("notion_api_token", '')
        )

        with st.form(key="notion_search_form", clear_on_submit=True, border=False):
            notion_url = st.text_input(
                "URL do Notion",
                key="notion_url",
                placeholder='Notion URL',
                autocomplete="off",
                help="Copie e cole a URL do Notion aqui."
            )

            if "profundidade_notion" not in st.session_state:
                st.session_state["profundidade_notion"] = 1

            profundidade_notion_atual = st.session_state["profundidade_notion"]

            profundidade = st.number_input(
                "Profundidade",
                min_value=-1,
                max_value=10,
                value=profundidade_notion_atual,
                placeholder="Profundidade da busca no Notion. -1 para buscar até o fim.",
                help="Profundidade da busca no Notion. -1 para buscar até o fim.",
            )

            # Input URL and Button
            buscar_notion = st.form_submit_button("Buscar", use_container_width=True)

        notion_nodes = st.session_state.get("notion_nodes", {})

        notion_container = st.empty()

        def create_multiselect(notion_multiselect_id):
            return notion_container.multiselect(
                "Urls do notion indexadas:",
                options=list(notion_nodes.items()),
                default=list(notion_nodes.items()),
                disabled=True,
                key="selected_node_urls_" + str(notion_multiselect_id),
                format_func=lambda x: x[1].object + ": " + x[0],
            )
        selected_nodes = create_multiselect(old_notion_counter)

        file_data = ""
        file_name = ""
        mime = "text/plain"

        if len(selected_nodes) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, mode="a", compression=zipfile.ZIP_STORED, allowZip64=True) as zip_file:
                for url, node in selected_nodes:
                    # conver the url to a valid file name
                    file_url = url.replace("/", "_").replace(":", "_").replace(".", "_")

                    if isinstance(node, DatabaseNode):
                        zip_file.writestr(f"{file_url}.csv", node.to_dataframe().to_csv().encode('utf-8'))
                    else:
                        zip_file.writestr(f"{file_url}.md", node.to_markdown())

            zip_buffer.seek(0)

            mime = "application/zip"
            file_data = zip_buffer.getvalue()
            file_name = f"notion_nodes_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        elif len(selected_nodes) == 1:
            url = selected_nodes[0][0]
            node = selected_nodes[0][1]

            if isinstance(node, DatabaseNode):
                file_data = node.to_dataframe().to_csv().encode('utf-8')
                file_name = f"{url}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
            else:
                file_data = node.to_markdown()
                file_name = f"{url}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"

        # download selected nodes
        st.download_button(
            label="Download",
            data=file_data,
            file_name=file_name,
            mime=mime,
            use_container_width=True,
        )

        if buscar_notion:
            if notion_url:
                st.session_state["profundidade_notion"] = profundidade

                kwargs = {}
                if profundidade != -1:
                    kwargs["max_depth"] = int(profundidade)

                with st.status("Indexando Notion..."):
                    try:
                        st.session_state["notion_api_key"] = notion_api_key
                        notion_reader = NotionReader(integration_token=notion_api_key)
                        notion_node = notion_reader.load_data(
                            notion_url,
                            **kwargs
                        )
                        notion_nodes[notion_url] = notion_node

                        # Update the session state with the fetched nodes
                        st.session_state["notion_nodes"] = notion_nodes

                        st.toast(f"🎉 Sucesso ao indexar a URL do Notion `{notion_url}`")

                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.toast("❌ Erro ao indexar o Notion. Verifique a URL e o token da API: " + str(e))
                        return

            else:
                st.toast("⚠️ Por favor, insira uma URL do Notion. ⚠️")

    if user_input_message and len(user_input_message) > 0 and len(selected_nodes) > 0:
        # remove the selected_nodes from st.session_state["notion_nodes"]
        for url, _ in selected_nodes:
            del st.session_state["notion_nodes"][url]

        st.session_state["notion_uploader_counter"] += 1
        new_input_counter = st.session_state["notion_uploader_counter"]
        create_multiselect(new_input_counter)

    if selected_nodes:
        transformed_notion_files = []

        for url, notion_node in selected_nodes:
            if isinstance(notion_node, DatabaseNode):
                transformed_notion_files.append(
                    PandasFile(f"Notion Database: {url}", notion_node.to_dataframe())
                )
            elif isinstance(notion_node, PageNode):
                content = notion_node.to_markdown().encode("utf-8")
                transformed_notion_files.extend([TextFile(f"Notion Page: {url}", notion_node.to_markdown(), "md")])
            else:
                content = notion_node.to_markdown().encode("utf-8")
                transformed_notion_files.extend([TextFile(f"Notion Block: {url}", content.to_markdown(), "md")])

        return transformed_notion_files

    return []
