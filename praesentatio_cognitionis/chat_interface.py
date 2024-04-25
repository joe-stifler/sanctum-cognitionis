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
        self.layout_initialized = False
        self.is_lazy_initial_message_set = False

    def setup_layout(self):
        self.settings_container = st.expander("Configurações atuais do modelo de inteligência artificial", expanded=False)

        with st.container(border=True):
            self.history = st.container(height=self.chat_height, border=False)
            st.markdown("---")
            self.input_prompt = st.chat_input("O que gostaria de perguntar?")

        self.layout_initialized = True
        self.print_initial_model_settings()

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

    def send_user_message(self, message_content, prefix_message_context=""):
        user_message = self.format_user_message(message_content)

        with self.history:
            self.add_message(self.user_name, user_message, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(user_message)

        self.send_ai_message(prefix_message_context + message_content)

    def format_ai_message(self, message_content):
        return self.ai_name + "\n\n" + message_content

    def send_ai_message(self, message_content):
        with self.history:
            with st.spinner("Seu professor(a) está processando sua mensagem..."):
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
                        st.error(f"Em caso de quota excedida (429 Quota Exceeded), aguarde dois minutos e tente novamente enviar sua mensagem.")

    def print_initial_model_settings(self):
        # Construct the message separately
        warning_message = (
            "## Configurações da Persona:\n"
            f"### **Nome da Persona:**\n{self.ai_name}\n"
            f"### **Avatar da Persona:**\n{self.ai_avatar}\n"
            "### **Prompt Base:**\n\n"
            f"```text\n{self.ai_base_prompt}\n```\n\n"
            "### Instruções:\n\n"
            "1. Digite uma mensagem no campo de entrada e pressione Enter para enviar.\n"
            "2. A IA começará a processar sua mensagem imediatamente e responderá em breve."
        )

        self.settings_container.info(warning_message)

    def reset_ai_chat(self, llm_family, persona_name, persona_description, persona_files, send_initial_message):
        persona_avatar="👩🏽‍🏫"
        persona_name=f':red[{persona_name}]'
        persona_files_str = self.convert_files_to_str(persona_files)
        persona_files = st.session_state["persona_settings"]["persona_files"]
        prompt_with_files_str = f"{persona_description}\n\n{persona_files_str}"
        persona_description = st.session_state["persona_settings"]["persona_description"]
        ai_model = llm_family.current_model()
        ai_base_prompt = prompt_with_files_str

        try:
            if "messages" not in st.session_state:
                st.session_state.messages = {}

            if self.session_id not in st.session_state.messages:
                st.session_state.messages[self.session_id] = {
                    "messages": [],
                    "ai_name": None,
                    "ai_avatar": None,
                }

            if send_initial_message:
                st.session_state.messages[self.session_id]["messages"] = []
                self.display_chat()

            self.ai_name = st.session_state.messages[self.session_id]["ai_name"]
            self.ai_avatar = st.session_state.messages[self.session_id]["ai_avatar"]
            self.message_history = st.session_state.messages[self.session_id]["messages"]

            self.ai_name = persona_name
            self.ai_avatar = persona_avatar
            self.ai_base_prompt = ai_base_prompt
            self.ai_model_name = ai_model.name
            self.ai_temperature = ai_model.temperature
            self.ai_max_output_tokens = ai_model.max_output_tokens

            self.message_history = []
            self.ai_model = ai_model.create_model()
            self.ai_chat = self.ai_model.start_chat(response_validation=False)

            if send_initial_message:
                self.is_lazy_initial_message_set = False
                self.send_ai_message(self.ai_base_prompt)
            else:
                self.is_lazy_initial_message_set = True
        except Exception as e:
            st.error(f"Erro ao configurar o modelo de IA: {e}")

    def convert_files_to_str(self, files_path: str):
        files_content = "## Arquivos disponíveis na base de conhecimento do professor(a):\n\n"
        files_content += "--------------------------------------------------------\n\n"

        for file_path in files_path:
            files_content += f"### Conteúdo do arquivo `{file_path}`:\n\n"

            with open(file_path, "r", encoding='utf-8') as file:
                files_content += file.read() + "\n\n"

        return files_content

    def run(self):
        try:
            self.display_chat()

            if self.input_prompt:
                message_context = ""

                if self.is_lazy_initial_message_set:
                    message_context = f"\n\n{self.ai_base_prompt}\n\n---\n\nAgora segue a mensagem inicial do estudante:\n\n"

                    self.is_lazy_initial_message_set = False

                self.send_user_message(
                    self.input_prompt,
                    prefix_message_context=message_context
                )

            with self.history:
                if self.is_lazy_initial_message_set:
                    st.info("O seu professor(a) está pronto para lhe ajudar. Tome a iniciativa e comece a sua interação com ele(a).")
        except Exception as e:
            st.error(f"Erro ao executar a interface de chat: {e}")
            pass
