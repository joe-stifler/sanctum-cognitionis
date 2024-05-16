# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_connector import ChatConnector

# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.gemini import GeminiDevFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the standard python environment
import json
import streamlit as st
import google.generativeai as genai

################################################################################
def get_llm_model(llm_model_default_name):
    llm_family = GeminiDevFamily()
    llm_model = llm_family.get_model(llm_model_default_name)

    return llm_model

def get_persona(persona_file):
    # load persona_file file content into a python dictionary
    with open(persona_file, 'r', encoding='utf-8') as file:
        persona_data = json.load(file)
        persona = Persona(**persona_data)

    return persona

def set_model(model_name, chat_connector, logger, google_api_key=None, notion_api_key=None):
    if "session_id" in st.session_state:
        chat_connector.delete_chat_history(st.session_state["session_id"])
        del st.session_state["session_id"]

    if google_api_key:
        genai.configure(api_key=google_api_key)
        st.session_state["google_api_key"] = google_api_key

    st.session_state["notion_api_token"] = notion_api_key

    # Initialize or fetch existing chat history
    persona_file = "dados/personas/professores/redacao/dani-stella/persona_config.json"
    persona = get_persona(persona_file)
    llm_model = get_llm_model(model_name)

    logger.info("Chosen Persona: %s", persona)
    logger.info("Chosen LLM Model: %s", llm_model)
    logger.info("Persona presenting yourself:\n\n%s", persona.present_yourself())
    chat_history = chat_connector.create_chat_history()
    chat_history.initialize_chat_message(llm_model, persona)
    logger.info("Creating chat history with session_id: %s", chat_history.session_id)


    st.session_state["session_id"] = chat_history.session_id


    st.toast("Modelo e Persona configurados com sucesso!")
    st.rerun()

def model_settings(chat_connector, logger):
    available_llms = ("GeminiDevModelPro1_5", "GeminiDevModelPro1_5_Flash")

    if "session_id" not in st.session_state:
        notion_api_key = None
        if "NOTION" in st.secrets:
            notion_api_key = st.secrets["NOTION"]["NOTION_API_KEY"]

        google_api_key = None
        if "GOOGLE_DEV" in st.secrets:
            google_api_key = st.secrets["GOOGLE_DEV"]["GOOGLE_API_KEY"]

        set_model(
            model_name=available_llms[1],
            chat_connector=chat_connector,
            logger=logger,
            notion_api_key=notion_api_key,
            google_api_key=google_api_key
        )

    with st.expander("Configurações do Modelo", expanded=False):
        model_name = st.selectbox(
            "Which model would you like to use?",
            available_llms,
            index=available_llms.index(st.session_state.get("model_name", available_llms[1]))
        )

        notion_api_key = st.text_input(
            "Token do Notion",
            key="ti_notion_api_token",
            type="password",
            value=st.session_state.get("notion_api_token", '')
        )

        google_api_key = st.text_input(
            "Token do Google AI",
            key="api_token",
            type="password",
            value=st.session_state.get("google_api_key", '')
        )
        atualizar_configuracoes = st.button("Atualizar Configurações")

        if atualizar_configuracoes:
            set_model(
                model_name=model_name,
                chat_connector=chat_connector,
                logger=logger,
                google_api_key=google_api_key,
                notion_api_key=notion_api_key
            )

    if "google_api_key" not in st.session_state:
        warning_message = "⚠️ Defina sua chave de API acima antes de iniciar a conversa."
        st.warning(warning_message)
        st.toast(warning_message)
