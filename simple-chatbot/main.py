import streamlit as st
from chat_session import ChatSession
from sql_connection import get_database_session  # Importe sua classe SQLiteConnection
import uuid
from llm_model import OllamaModel, GeminiModel

st.title("Chat with Gemini or Ollama")

conn = get_database_session()

# Choose LLM family
llm_family = st.selectbox(
    "Choose an LLM family:",
    ("Ollama", "Gemini"),
)

# Choose model based on LLM family
if llm_family == "Gemini":
    model_choice = "gemini-1.5-flash"
elif llm_family == "Ollama":
    model_choice = st.selectbox(
        "Choose an Ollama model:", ("gemma:2b", "gemma:7b", "llama3:latest")
    )

# Get Gemini API key
gemini_api_key = st.text_input(
    "Enter your Gemini API key (required for Gemini)", type="password"
)

# Create a ChatState object
if "chat_session" not in st.session_state:
    if llm_family == "Gemini" and gemini_api_key:
        st.session_state.chat_session = ChatSession(
            model=GeminiModel(model_name=model_choice, api_key=gemini_api_key),
            sqlite_conn=conn,
        )
    elif llm_family == "Ollama":
        st.session_state.chat_session = ChatSession(
            model=OllamaModel(model_name=model_choice), sqlite_conn=conn
        )
    else:
        st.warning("Please enter your Gemini API key if you want to use Gemini.")

chat_session = st.session_state.chat_session

# Retrieve chat history from database
chat_history = chat_session.get_history()

# Display chat messages from history
for role, message in chat_history:
    with st.chat_message(role):
        st.markdown(message)

# Accept user input
if prompt := st.chat_input("Ask me anything!"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send prompt to chosen model and stream response
    with st.chat_message("assistant"):
        response_stream = chat_session.send_stream_message(prompt)
        response = st.write_stream(response_stream)
