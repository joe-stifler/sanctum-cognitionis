import csv
import functools
import streamlit as st

class ChatInterface:
    def __init__(self, session_id, user_name, user_avatar, chat_height=400):
        print("ChatInterface.__init__()")
        
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

    def setup_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = {}

        if self.session_id not in st.session_state.messages:
            st.session_state.messages[self.session_id] = {
                "messages": [],
                "ai_name": None,
                "ai_avatar": None,
            }

        self.ai_name = st.session_state.messages[self.session_id]["ai_name"]
        self.ai_avatar = st.session_state.messages[self.session_id]["ai_avatar"]
        self.message_history = st.session_state.messages[self.session_id]["messages"]

    def setup_ai(self, ai_model, ai_name, ai_avatar, ai_base_prompt):
        try:
            self.ai_name = ai_name
            self.ai_avatar = ai_avatar
            self.ai_base_prompt = ai_base_prompt
            self.ai_model_name = ai_model.name
            self.ai_temperature = ai_model.temperature
            self.ai_max_output_tokens = ai_model.max_output_tokens

            self.message_history = []
            self.ai_model = ai_model.create_model()
            self.ai_chat = self.ai_model.start_chat(response_validation=False)

            st.session_state.messages[self.session_id]["ai_name"] = ai_name
            st.session_state.messages[self.session_id]["ai_avatar"] = ai_avatar
            st.session_state.messages[self.session_id]["messages"] = self.message_history

            self.send_ai_message(self.ai_base_prompt)
        except Exception as e:
            st.error(f"Erro ao configurar o modelo de IA: {e}")

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

    def format_user_message(self, message_content):
        return self.user_name + "\n\n" + message_content + "\n"

    def send_user_message(self, message_content, message_context=""):
        user_message = self.format_user_message(message_content)

        with self.history:
            self.add_message(self.user_name, user_message, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(user_message)

        self.send_ai_message(message_context + message_content)

    def format_ai_message(self, message_content):
        return self.ai_name + "\n\n" + message_content

    def send_ai_message(self, message_content):
        with self.history:
            with st.spinner("A IA está processando a mensagem..."):
                with st.chat_message(self.ai_name, avatar=self.ai_avatar):
                    try:
                        responses = self.ai_chat.send_message(message_content, stream=True)

                        def format_response(responses):
                            yield self.ai_name + "\n\n"

                            for response in responses:
                                print("\n\nInformação sobre a resposta da IA:")
                                print("--------------------------------")
                                print("Resposta da IA:", type(response))
                                print("Prompt Feedback:", response.prompt_feedback)
                                print("Usage Metadata:", response.usage_metadata)

                                context_error = "Isto pode ser um problema com o modelo de IA. Tente re-enviar sua mensagem ou mudar elementos de sua pergunta. E lembre-se: estes modelos de IA são muito recentes. Então apesar de não ser o ideal, erros assim acontecerão ocasionamente até que a tecnologia amadureça."

                                if len(response.candidates) == 0:
                                    print("A resposta está vazia.")
                                    yield f":red[Erro: a resposta gerado pela está vazia. {context_error}]"
                                    continue

                                candidate = response.candidates[0]

                                print("\n\nInformation about the candidate:")
                                print("--------------------------------")
                                print("Index: `", candidate.index, "`")
                                print("Content: `", candidate.content, "`")
                                print("Finish Reason: `", candidate.finish_reason, "`")
                                print("Safety Ratings: `", candidate.safety_ratings, "`")
                                print("Function Calls: `", candidate.function_calls, "`")
                                print("Prompt Feedback: `", candidate.finish_message, "`")
                                print("Citation Metadata: `", candidate.citation_metadata, "`")

                                if hasattr(candidate, "text"):
                                    yield candidate.text
                                    continue
    
                                if candidate.finish_reason == "FINISH_REASON_MAX_TOKENS":
                                    yield candidate.text + "\n\n:yellow[Nota: Resposta truncada devido ao limite de tokens.]\n\n"
                                elif candidate.finish_reason == "FINISH_REASON_SAFETY":
                                    print("A resposta foi interrompida por motivos de segurança.")
                                    yield ":red[Erro: A resposta contém conteúdo inapropriado.]\n\n"
                                elif candidate.finish_reason == "FINISH_REASON_RECITATION":
                                    print("A resposta foi interrompida devido a citações não autorizadas.")
                                    yield ":red[Erro: A resposta contém citações não autorizadas.]\n\n"
                                elif candidate.finish_reason == "FINISH_REASON_UNSPECIFIED":
                                    print("A resposta foi interrompida por um motivo não especificado.")
                                    yield ":red[Erro: Motivo da interrupção não especificado.]\n\n"
                                else:
                                    print(f"A resposta foi interrompida por um motivo desconhecido: {candidate.finish_reason}.")
                                    yield f":red[Erro: Motivo da interrupção desconhecido ({candidate.finish_reason}). {context_error}]\n\n"

                                print("-------------------------------------------------")

                        responses_generator = format_response(responses)
                        streamed_response = st.write_stream(responses_generator)
                        self.add_message(self.ai_name, streamed_response, self.ai_avatar, is_user=False)
                    except Exception as e:
                        print(f"Erro ao enviar mensagem para a IA: {e}")
                        st.error(f"Erro ao processar a mensagem: {e}")

    def print_initial_model_settings(self):
        # Construct the message separately
        warning_message = (
            "## Bem-vindo! 🤖\n\n"
            "O modelo de IA foi inicializado corretamente e está pronto para receber mensagens.\n\n"
            # "## Configurações do modelo:\n"
            # f"### **Nome do modelo:**\n{self.ai_model_name}\n"
            # f"### **Máximo de tokens na saída:**\n{self.ai_max_output_tokens}\n"
            # f"### **Temperatura:**\n{self.ai_temperature}\n\n"
            "## Configurações da Persona:\n"
            f"### **Nome da Persona:**\n{self.ai_name}\n"
            f"### **Avatar da Persona:**\n{self.ai_avatar}\n"
            "### **Prompt Base:**\n\n"
            f"```text\n{self.ai_base_prompt}\n```\n\n"
            # "### **Arquivos na Base de Conhecimento:**\n\n"
            # f"{ai_files_table}\n\n"
            "### Instruções:\n\n"
            "1. Digite uma mensagem no campo de entrada e pressione Enter para enviar.\n"
            "2. A IA começará a processar sua mensagem imediatamente e responderá em breve."
        )
        
        # Display the message
        self.settings_container.info(warning_message)


    def run(self):
        try:
            self.print_initial_model_settings()

            self.display_chat()

            if self.input_prompt:
                self.send_user_message(self.input_prompt)
        except Exception as e:
            st.error(f"Erro ao executar a interface de chat: {e}")
            pass
