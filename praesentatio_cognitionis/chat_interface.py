import streamlit as st

class ChatInterface:
    def __init__(self, session_id, user_name, user_avatar, chat_height=400):
        self.user_name = user_name
        self.user_avatar = user_avatar
        self.chat_height = chat_height
        self.session_id = session_id
        self.message_history = []
        
        # model objects
        self.ai_chat = None
        self.ai_model = None
        
        # model settings attributes
        self.ai_model_name = None
        self.ai_max_output_tokens = None
        self.ai_temperature = None

        # persona attributes
        self.ai_name = None
        self.ai_files = None
        self.ai_avatar = None
        self.ai_base_prompt = None
        
        self.settings_container = None

    def setup_ai(self, ai_model, ai_name, ai_avatar, ai_base_prompt, ai_files, force_reset=False):
        if "messages" not in st.session_state:
            st.session_state.messages = {}

        if self.session_id not in st.session_state.messages:
            st.session_state.messages[self.session_id] = {
                "messages": [],
                "ai_chat": None,
                "ai_model": None,

                "ai_model_name": None,
                "ai_model_temperature": None,
                "ai_model_max_output_tokens": None,

                "ai_name": None,
                "ai_avatar": None,
                "ai_files": None,
                "ai_base_prompt": None
            }

        if force_reset:
            self.ai_name = ai_name
            self.ai_avatar = ai_avatar
            self.ai_files = ai_files
            self.ai_base_prompt = ai_base_prompt
            
            st.session_state.messages[self.session_id]["ai_name"] = ai_name
            st.session_state.messages[self.session_id]["ai_avatar"] = ai_avatar
            st.session_state.messages[self.session_id]["ai_files"] = ai_files
            st.session_state.messages[self.session_id]["ai_base_prompt"] = ai_base_prompt

            self.ai_model_name = ai_model.name
            self.ai_temperature = ai_model.temperature
            self.ai_max_output_tokens = ai_model.max_output_tokens
            
            st.session_state.messages[self.session_id]["ai_model_name"] = self.ai_model_name
            st.session_state.messages[self.session_id]["ai_model_temperature"] = ai_model.temperature
            st.session_state.messages[self.session_id]["ai_model_max_output_tokens"] = ai_model.max_output_tokens

            self.message_history = []
            self.ai_model = ai_model.create_model()
            self.ai_chat = self.ai_model.start_chat(response_validation=False)

            st.session_state.messages[self.session_id]["ai_chat"] = self.ai_chat
            st.session_state.messages[self.session_id]["ai_model"] = self.ai_model
            st.session_state.messages[self.session_id]["messages"] = self.message_history
            
            self.send_ai_message([self.ai_base_prompt] + self.ai_files)

        self.ai_name = st.session_state.messages[self.session_id]["ai_name"]
        self.ai_avatar = st.session_state.messages[self.session_id]["ai_avatar"]
        self.ai_files = st.session_state.messages[self.session_id]["ai_files"]
        self.ai_base_prompt = st.session_state.messages[self.session_id]["ai_base_prompt"]

        self.ai_model_name = st.session_state.messages[self.session_id]["ai_model_name"]
        self.ai_temperature = st.session_state.messages[self.session_id]["ai_model_temperature"]
        self.ai_max_output_tokens = st.session_state.messages[self.session_id]["ai_model_max_output_tokens"]
        self.ai_chat = st.session_state.messages[self.session_id]["ai_chat"]
        self.ai_model = st.session_state.messages[self.session_id]["ai_model"]
        self.message_history = st.session_state.messages[self.session_id]["messages"]

    def setup_layout(self):
        with st.container(border=True):
            self.history = st.container(height=self.chat_height, border=False)
            self.input_prompt = st.chat_input("O que gostaria de perguntar?")
            
        self.settings_container = st.expander("Configurações do modelo de IA", expanded=False)

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
            for message in self.message_history:
                with st.chat_message(message["role"], avatar=message["avatar"]):
                    st.markdown(message["content"])

    def check_chat_state(self):
        if self.ai_chat is None or self.ai_model is None:
            with self.history:
                st.error("Por favor, inicialize o modelo de IA antes de enviar mensagens.")

            return False
        return True

    def format_user_message(self, message_content):
        return self.user_name + "\n\n" + message_content + "\n"

    def send_user_message(self, message_content):
        user_message = self.format_user_message(message_content)

        with self.history:
            self.add_message(self.user_name, user_message, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(user_message)

    def format_ai_message(self, message_content):
        return self.ai_name + "\n\n" + message_content

    def send_ai_message(self, message_content):
        with self.history:
            with st.spinner("A IA está processando a mensagem..."):
                with st.chat_message(self.ai_name, avatar=self.ai_avatar):
                    try:
                        responses = self.ai_chat.send_message(message_content, stream=True)
                        
                        def format_response(response):
                            yield self.ai_name + "\n\n"
                            
                            for response in responses:
                                yield response.text

                        respones_generator = format_response(responses)
                        streamed_response = st.write_stream(respones_generator)
                        self.add_message(self.ai_name, streamed_response, self.ai_avatar, is_user=False)
                    except Exception as e:
                        st.error(f"Erro ao processar a mensagem: {e}")

    def print_initial_model_settings(self):
        # Format the list into a Markdown table
        if self.ai_files:
            ai_files_table = "| Arquivo |\n| --- |\n" + '\n'.join(f"| {file} |" for file in self.ai_files)
        else:
            ai_files_table = "Nenhum arquivo carregado."

        # Construct the message separately
        warning_message = (
            "## Bem-vindo! 🤖\n\n"
            "O modelo de IA foi inicializado corretamente e está pronto para receber mensagens.\n\n"
            "## Configurações do modelo:\n"
            f"### **Nome do modelo:**\n{self.ai_model_name}\n"
            f"### **Máximo de tokens na saída:**\n{self.ai_max_output_tokens}\n"
            f"### **Temperatura:**\n{self.ai_temperature}\n\n"
            "## Configurações da Persona:\n"
            f"### **Nome da Persona:**\n{self.ai_name}\n"
            f"### **Avatar da Persona:**\n{self.ai_avatar}\n"
            "### **Prompt base:**\n\n"
            f"```text\n{self.ai_base_prompt}\n```\n\n"
            "### **Arquivos na Base de Conhecimento:**\n\n"
            f"{ai_files_table}\n\n"
            "### Instruções:\n\n"
            "1. Digite uma mensagem no campo de entrada e pressione Enter para enviar.\n"
            "2. A IA começará a processar sua mensagem imediatamente e responderá em breve."
        )
        
        # Display the message
        self.settings_container.info(warning_message)
        

    def run(self):
        if not self.check_chat_state():
            return

        self.print_initial_model_settings()

        self.display_chat()

        if self.input_prompt:
            self.send_user_message(self.input_prompt)
            self.send_ai_message(self.input_prompt)
