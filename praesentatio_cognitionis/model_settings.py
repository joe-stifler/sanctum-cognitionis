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
    with open(persona_file, "r", encoding="utf-8") as file:
        persona_data = json.load(file)
        persona = Persona(**persona_data)

    return persona


def set_model(
    persona_name, persona_file, model_name, chat_connector, logger, google_api_key=None
):
    if "session_id" in st.session_state:
        chat_connector.delete_chat_history(st.session_state["session_id"])
        del st.session_state["session_id"]

    if google_api_key:
        genai.configure(api_key=google_api_key)
        st.session_state["google_api_key"] = google_api_key

    # Initialize or fetch existing chat history
    persona = get_persona(persona_file)
    llm_family = GeminiDevFamily()
    llm_model = llm_family.get_model(model_name)

    logger.info("Chosen Persona: %s", persona)
    logger.info("Chosen LLM Model: %s", llm_model)
    logger.info("Persona presenting yourself:\n\n%s", persona.present_yourself())

    chat_history = chat_connector.create_chat_history()
    chat_history.initialize_chat_message(llm_model, persona)

    logger.info("Creating chat history with session_id: %s", chat_history.session_id)

    st.session_state["model_name"] = model_name
    st.session_state["persona_name"] = persona_name
    st.session_state["persona_file"] = persona_file
    st.session_state["session_id"] = chat_history.session_id

    st.rerun()


def model_settings(chat_connector, logger):
    available_personas = {
        "Lumi: your personal research companion": "dados/personas/lumi-english/persona_config.json",
        "Gemini 1.5": "dados/personas/gemini-1_5/persona_config.json",
        "Pensador Profundo": "dados/personas/persador_profundo/persona_config.json",
        "Dani Stella (a inteligência artificial)": "dados/personas/dani-stella/persona_config.json",
    }

    available_models = ["GeminiDevModelPro1_5", "GeminiDevModelPro1_5_Flash"]

    if "session_id" not in st.session_state:
        google_api_key = None
        if "GOOGLE_DEV" in st.secrets:
            google_api_key = st.secrets["GOOGLE_DEV"]["GOOGLE_API_KEY"]

        persona_name = "Lumi: your personal research companion"
        model_name = "GeminiDevModelPro1_5_Flash"

        set_model(
            persona_name=persona_name,
            persona_file=available_personas[persona_name],
            model_name=model_name,
            chat_connector=chat_connector,
            logger=logger,
            google_api_key=google_api_key,
        )

    with st.expander("Model Settings", expanded=False):
        available_persona_names = list(available_personas.keys())
        persona_name = st.selectbox(
            "Choose your preferred persona",
            available_persona_names,
            index=available_persona_names.index(
                st.session_state.get(
                    "persona_name", "Lumi: your personal research companion"
                )
            ),
        )

        model_name = st.selectbox(
            "Choose your preferred model",
            available_models,
            index=available_models.index(
                st.session_state.get("model_name", "GeminiDevModelPro1_5_Flash")
            ),
        )

        google_api_key = st.text_input(
            "Set your Google Gemini API Key",
            key="api_token",
            type="password",
            help="Follow the instructions in the [official website](https://makersuite.google.com/app/apikey) to create a new API Key",
            value=st.session_state.get("google_api_key", ""),
        )
        atualizar_configuracoes = st.button("Update Settings")

        if atualizar_configuracoes:
            set_model(
                persona_name=persona_name,
                persona_file=available_personas[persona_name],
                model_name=model_name,
                chat_connector=chat_connector,
                logger=logger,
                google_api_key=google_api_key,
            )

    if "google_api_key" not in st.session_state:
        return False

    return True
