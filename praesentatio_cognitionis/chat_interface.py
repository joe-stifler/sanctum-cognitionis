import streamlit as st

class ChatInterface:
    def __init__(self, session_id, user_name, user_avatar, ai_name, ai_avatar, ai_first_message=None, chat_height=400):
        self.user_name = user_name
        self.user_avatar = user_avatar
        self.ai_name = ai_name
        self.chat_height = chat_height
        self.ai_avatar = ai_avatar
        self.session_id = session_id
        self.ai_first_message = ai_first_message
        self.setup()

    def setup(self):
        with st.container(border=True):
            # Initialize chat history container
            self.history = st.container(height=self.chat_height, border=False)
            self.input_prompt = st.chat_input("O que gostaria de perguntar?")

            # Initialize session state for messages if not already present
            if "messages" not in st.session_state:
                st.session_state.messages = {}

            if self.session_id not in st.session_state.messages:
                st.session_state.messages[self.session_id] = [{
                    "role": self.ai_name,
                    "content": self.ai_first_message,
                    "avatar": self.ai_avatar,
                    "is_user": False
                }]
            
            self.message_history = st.session_state.messages[self.session_id]

    def add_message(self, role, content, avatar, is_user):
        self.message_history.append(
            {
                "role": role,
                "content": content,
                "avatar": avatar,
                "is_user": is_user
            }
        )

    def display_chat(self):
        with self.history:
            # Display chat messages from history            
            for message in self.message_history:
                with st.chat_message(message["role"], avatar=message["avatar"]):
                    st.markdown(message["content"])
                    st.divider()

    def send_user_message(self, message_content):
        with self.history:
            self.add_message(self.user_name, message_content, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(message_content)
                st.divider()

    def send_ai_message(self, message_content):
        with self.history:
            self.add_message(self.ai_name, message_content, self.ai_avatar, is_user=False)
            with st.chat_message(self.ai_name, avatar=self.ai_avatar):
                st.markdown(message_content)
                st.divider()

    def run(self):
        self.display_chat()

        if self.input_prompt:
            self.send_user_message(self.input_prompt)
            ai_response = "Estou processando sua solicitação..."
            self.send_ai_message(ai_response)
