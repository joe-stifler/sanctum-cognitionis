import streamlit as st
from langsmith import Client

class ChatInterface:
    def __init__(self, session_id, user_name, user_avatar, chat_height=400, username=""):
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

        self.langsmith_client = None
        self.langsmith_dataset = None
        self.username = username

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
            if len(self.message_history) == 0:
                st.markdown("")
            
            for idx, message in enumerate(self.message_history):
                with st.chat_message(message["role"], avatar=message["avatar"]):
                    st.markdown(message["content"])
                    
                    if idx < len(self.message_history) - 1:
                        st.divider()

    def format_user_message(self, message_content):
        return self.user_name + "\n\n" + message_content + "\n"

    def send_user_message(self, message_content, prefix_message_context=""):
        user_message = self.format_user_message(message_content)

        message_context = ""
        if self.is_lazy_initial_message_set:
            first__message_context = f"\n\n{self.ai_base_prompt}"
            self.send_ai_message(first__message_context)

            self.is_lazy_initial_message_set = False

        with self.history:
            self.add_message(self.user_name, user_message, self.user_avatar, is_user=True)
            with st.chat_message(self.user_name, avatar=self.user_avatar):
                st.markdown(user_message)

        if len(prefix_message_context) > 0:
            message_context += "---\n\nContexto do input do estudante:\n\n" + prefix_message_context

        self.send_ai_message(message_context + message_content)

    def format_ai_message(self, message_content):
        return self.ai_name + "\n\n" + message_content

    def send_ai_message(self, message_content):
        with self.history:
            outputs = []

            with st.spinner("Seu professor(a) está processando sua mensagem..."):
                with st.chat_message(self.ai_name, avatar=self.ai_avatar):
                    try:
                        responses = self.ai_chat.send_message(message_content, stream=True)

                        def format_response(responses):
                            yield self.ai_name + "\n\n"

                            for index, response in enumerate(responses):
                                outputs.append(
                                    {   
                                        "index": index,
                                        "usage_metadata": str(response.usage_metadata),
                                        "candidates": [str(response.candidates) for candidate in response.candidates]
                                    }
                                )
                                
                                print("\n\nInformação sobre a resposta da IA:")
                                print("--------------------------------")
                                print("Resposta da IA:", type(response))
                                print("Prompt Feedback:", str(response.prompt_feedback))
                                print("Usage Metadata:", str(response.usage_metadata))

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
                                elif candidate.finish_reason == "FINISH_REASON_STOP":
                                    yield "\n\n"
                                elif candidate.finish_reason == "FINISH_REASON_MAX_TOKENS":
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
                        self.langsmith_client.create_example(
                            inputs={"question": message_content},
                            outputs={"answer": outputs},
                            dataset_id=self.langsmith_dataset.id
                        )
                    except Exception as e:
                        outputs.append(
                            {
                                "error": str(e)
                            }
                        )
                        print(f"Erro ao enviar mensagem para a IA: {e}")
                        st.error(f"Erro ao processar a mensagem: {e}")
                        self.langsmith_client.create_example(
                            inputs={"question": message_content},
                            outputs={"answer": outputs},
                            dataset_id=self.langsmith_dataset.id
                        )

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
        self.message_history = []

        if send_initial_message:
            self.display_chat()

        ai_model = llm_family.current_model()

        persona_avatar="👩🏽‍🏫"
        persona_name=f':red[{persona_name}]'
        persona_files_str = self.convert_files_to_str(persona_files)
        prompt_with_files_str = f"{persona_files_str}\n\n---\n\n{persona_description}"
        ai_base_prompt = prompt_with_files_str

        try:
            self.ai_name = persona_name
            self.ai_avatar = persona_avatar
            self.ai_base_prompt = ai_base_prompt
            self.ai_model_name = ai_model.name
            self.ai_temperature = ai_model.temperature
            self.ai_max_output_tokens = ai_model.max_output_tokens
            self.ai_model = ai_model.create_model()
            self.ai_chat = self.ai_model.start_chat(response_validation=False)

            self.langsmith_client = Client()
            dataset_name = f"Conversation with '{self.username}'"
            datasets = self.langsmith_client.list_datasets(dataset_name=dataset_name)
            datasets = [dataset for dataset in datasets]

            if len(datasets) == 0:
                self.langsmith_dataset = self.langsmith_client.create_dataset(dataset_name)
            else:
                self.langsmith_dataset = datasets[0]

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

            extension = file_path.split(".")[-1]
            with open(file_path, "r", encoding='utf-8') as file:
                files_content += f"```{extension}\n" + file.read() + "\n```\n\n"

        return files_content

    def run(self):
        try:
            self.display_chat()

            if self.input_prompt:
                message_context = ""
                user_message = "\n\n---\n\nInput do estudante:\n\n" + self.input_prompt
                self.send_user_message(
                    user_message,
                    prefix_message_context=message_context
                )

            with self.history:
                if self.is_lazy_initial_message_set:
                    st.info("O seu professor(a) está pronto para lhe ajudar. Tome a iniciativa e comece a sua interação com ele(a).")
        except Exception as e:
            st.error(f"Erro ao executar a interface de chat: {e}")
            pass
