import streamlit as st
from chat_session import ChatSession
from sql_connection import get_database_session  # Import your SQLiteConnection class
from llm_model import OllamaModel, GeminiModel

conn = get_database_session()

# Create the ChatSession object (only once)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = ChatSession(connection=conn)

chat_session = st.session_state.chat_session

# Create an expander for settings
with st.expander("Settings"):
    # Choose LLM family
    llm_family = st.selectbox(
        "Choose an LLM family:",
        ("Ollama", "Gemini"),
    )

    # Choose model based on LLM family
    if llm_family == "Gemini":
        model_choice = "gemini-1.5-flash"
        model_choice = st.selectbox(
            "Choose a Gemini model:",
            ("gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-1.0-pro"),
        )
        # Get Gemini API key
        gemini_api_key = st.text_input(
            "Enter your Gemini API key (required for Gemini)", type="password"
        )
    elif llm_family == "Ollama":
        model_choice = st.selectbox(
            "Choose an Ollama model:", ("gemma:2b", "gemma:7b", "llama3:latest")
        )

    # Button to update chat settings
    if st.button("Update Chat Settings"):
        if llm_family == "Gemini" and gemini_api_key:
            chat_session.update_model(
                GeminiModel(model_name=model_choice, api_key=gemini_api_key)
            )
        elif llm_family == "Ollama":
            chat_session.update_model(OllamaModel(model_name=model_choice))
        else:
            st.warning("Please enter your Gemini API key if you want to use Gemini.")

# Retrieve chat history from database
chat_history = chat_session.get_history()

# Display chat messages from history
for role, message in chat_history:
    with st.chat_message(role):
        st.markdown(message)

prompt_input = st.chat_input("Ask me anything!")

if not chat_session.is_model_initialized():
    st.warning("Please select a model and update chat settings.")
    st.stop()

# Accept user input
if prompt_input:
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt_input)

    # Send prompt to chosen model and stream response
    with st.chat_message("assistant"):
        try:
            response_stream = chat_session.send_stream_message(prompt_input)
            response = st.write_stream(response_stream)
        except Exception as e:
            st.error(str(e))
