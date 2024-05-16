from praesentatio_cognitionis.chat_history import ChatHistory

import uuid
import streamlit as st

class ChatConnector:
    def __init__(self):
        self.chats = {}

    def create_chat_history(self):
        session_id = str(uuid.uuid4().hex)

        if session_id in self.chats:
            assert False, f"Chat with session_id {session_id} already exists"

        self.chats[session_id] = ChatHistory(session_id)

        return self.chats[session_id]

    def delete_chat_history(self, session_id):
        if session_id not in self.chats:
            assert False, f"Chat with session_id {session_id} not found"
        del self.chats[session_id]

    def fetch_chat_history(self, session_id):
        if session_id not in self.chats:
            assert False, f"Chat with session_id {session_id} not found"
        return self.chats[session_id]


@st.cache_resource
def create_chat_connector():
    return ChatConnector()
