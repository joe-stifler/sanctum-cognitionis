# module imports from the servitium_cognitionis package
from servitium_cognitionis.llms.gemini import GeminiDevFamily
from servitium_cognitionis.personas.persona_base import Persona

# module imports from the standard python environment
import time
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
    persona_name,
    persona_file,
    model_name,
    chat_connector,
    logger,
    temperature,
    google_api_key=None,
):
    if "session_id" in st.session_state:
        chat_connector.delete_chat_history(st.session_state["session_id"])
        del st.session_state["session_id"]

    if google_api_key:
        genai.configure(api_key=google_api_key)
        st.session_state["google_api_key"] = google_api_key

    # Initialize or fetch existing chat history
    persona = get_persona(persona_file)
    persona.temperature = temperature  # Update persona's temperature
    persona.model = model_name

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
    st.session_state["session_id"] = chat_history.session_id
    st.session_state["temperature"] = temperature

    st.rerun()


def model_settings(
    chat_connector, logger, google_api_key=None, persona_name=None, model_name=None
):
    available_personas = {
        "Lumi: your personal research companion": "dados/personas/lumi/persona_config.json",
        "Ryan: your personal python, deep learning, statistician, mathematician, and cryptography expert": "dados/personas/ryan/persona_config.json",
        "Dani Stella (a inteligência artificial)": "dados/personas/dani-stella/persona_config.json",
        "Gemini 1.5": "dados/personas/gemini-1_5/persona_config.json",
        "Pensador Profundo": "dados/personas/persador_profundo/persona_config.json",
    }

    default_model_name = "GeminiDevModel1_5_Flash"
    default_persona_name = "Lumi: your personal research companion"
    available_models = ["GeminiDevModelPro1_5", "GeminiDevModel1_5_Flash"]

    if "session_id" not in st.session_state:
        # If the URL parameters are available, use them
        if google_api_key:
            st.session_state["google_api_key"] = google_api_key
        if persona_name:
            st.session_state["persona_name"] = persona_name
        if model_name:
            st.session_state["model_name"] = model_name

        # If the URL parameters are not available, use the default values
        if "google_api_key" not in st.session_state:
            if "GOOGLE_DEV" in st.secrets:
                st.session_state["google_api_key"] = st.secrets["GOOGLE_DEV"][
                    "GOOGLE_API_KEY"
                ]

        if "persona_name" not in st.session_state:
            st.session_state["persona_name"] = default_persona_name

        if "model_name" not in st.session_state:
            st.session_state["model_name"] = default_model_name

        persona_name = st.session_state.get("persona_name", default_persona_name)

        # Check if the persona exists in the available personas
        if persona_name in available_personas:
            persona = get_persona(available_personas[persona_name])

            set_model(
                persona_name=persona_name,
                persona_file=available_personas[persona_name],
                model_name=st.session_state.get("model_name", default_model_name),
                chat_connector=chat_connector,
                logger=logger,
                temperature=persona.temperature,  # Use persona's temperature as default
                google_api_key=st.session_state.get("google_api_key", ""),
            )
        else:
            if persona_name:
                st.error(
                    f"The persona '{persona_name}' was not found. Using the default persona '{default_persona_name}' instead."
                )
                time.sleep(3)

            # If the persona does not exist, use the default persona
            st.session_state["persona_name"] = default_persona_name
            st.session_state["model_name"] = default_model_name

            default_persona = get_persona(available_personas[default_persona_name])

            set_model(
                persona_name=default_persona_name,
                persona_file=available_personas[default_persona_name],
                model_name=default_model_name,
                chat_connector=chat_connector,
                logger=logger,
                temperature=default_persona.temperature,
                google_api_key=st.session_state.get("google_api_key", ""),
            )
            st.success(
                f"The persona '{persona_name}' was not found. Using the default persona '{default_persona_name}' instead."
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
                st.session_state.get("model_name", default_model_name)
            ),
        )

        temperature = st.slider(
            "Choose the model temperature",
            min_value=0.0,
            max_value=2.0,
            step=0.01,  # Adjust step if needed, e.g., 0.5 for larger increments
            value=st.session_state.get(
                "temperature", 1.0
            ),  # Use session state value as default
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
                temperature=temperature,  # Pass the slider value to the persona
            )

    if "google_api_key" not in st.session_state:
        return False

    return True
