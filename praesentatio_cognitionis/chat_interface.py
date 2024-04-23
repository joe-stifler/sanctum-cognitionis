import streamlit as st

class ChatInterface:
    def __init__(self, session_id, user_name, user_avatar, chat_height=400):
        self.user_name = user_name
        self.user_avatar = user_avatar
        self.chat_height = chat_height
        self.session_id = session_id
        self.message_history = []
        self.ai_model = None

    def setup_ai(self, ai_model, ai_name, ai_avatar, ai_base_prompt, ai_files, ai_default_chat_message=None, force_reset=False):
        self.ai_name = ai_name
        self.ai_avatar = ai_avatar

        # Initialize session state for messages if not already present
        if "messages" not in st.session_state:
            st.session_state.messages = {}

        if self.session_id not in st.session_state.messages or force_reset:
            st.session_state.messages[self.session_id] = {
                "ai_model": None,
                "messages": [{
                    "role": self.ai_name,
                    "avatar": self.ai_avatar,
                    "is_user": False,
                    "content": self.format_ai_message(ai_default_chat_message),
                }]
            }

        self.message_history = st.session_state.messages[self.session_id]["messages"]

    def setup_layout(self):
        with st.container(border=True):
            self.history = st.container(height=self.chat_height, border=False)
            self.input_prompt = st.chat_input("O que gostaria de perguntar?")

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

    def format_user_message(self, message_content):
        return self.user_name + "\n\n" + message_content + "\n"

    def format_ai_message(self, message_content):
        return self.ai_name + "\n\n" + message_content

    def send_user_message(self, message_content):
        user_message = self.format_user_message(message_content)

        with self.history:
            self.add_message(self.user_name, user_message, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(user_message)

    def send_ai_message(self, message_content):
        ai_message = self.format_ai_message(message_content)

        with self.history:
            self.add_message(self.ai_name, ai_message, self.ai_avatar, is_user=False)
            with st.chat_message(self.ai_name, avatar=self.ai_avatar):
                st.markdown(ai_message)

    def run(self):
        self.display_chat()

        if self.input_prompt:
            self.send_user_message(self.input_prompt)
            ai_response = f"Estou processando sua solicitação... {self.input_prompt}"
            self.send_ai_message(ai_response)
