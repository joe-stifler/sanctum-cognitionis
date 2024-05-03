from servitium_cognitionis.llms.base import LLMBaseModel

from vertexai import generative_models
from vertexai.generative_models import Part, Image
from vertexai.generative_models import GenerativeModel, FinishReason

class LLMGeminiBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_instance = None
        self._model_chats = {}

    def initialize_model(self, system_instruction=[], temperature=None, max_output_tokens=None):
        self._model_instance = GenerativeModel(
            model_name=self.name,
            generation_config={
                "temperature": temperature if temperature else self.temperature,
                "max_output_tokens": max_output_tokens if max_output_tokens else self.max_output_tokens,
            },
            system_instruction=system_instruction,
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        )

    def create_chat(self, session_id):
        if self._model_instance is None:
            raise ValueError("Model has not been initialized. Call initialize_model() first")

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = self._model_instance.start_chat(response_validation=False)

    def process_file(self, files):
        gemini_files = []
        
        if len(files) == 0:
            return gemini_files

        gemini_files.append("Abaixo segue todos os arquivos associados com a mensagem do usuário:\n\n")

        for file_path, byte_values in files:
            extension = file_path.split(".")[-1]

            if extension in ["jpg", "jpeg", "png"]:
                gemini_files.append(f"abaixo segue o arquivo {extension} `{file_path}`:\n")
                gemini_files.append(Image.from_bytes(byte_values))
            elif extension in ["txt"]:
                gemini_files.append(f"abaixo segue o arquivo {extension} `{file_path}`:\n")
                gemini_files.append(Part.from_bytes(byte_values))
            else:
                
                raise ValueError(f"Formato de arquivo não suportado: {extension}")

        if len(gemini_files) != 0:
            gemini_files.append("\n\n---\n\n")

        return gemini_files

    def format_message(self, message, files):
        return self.process_file(files) + ["Abaixo segue a mensagem do usuário:\n\n" + message]

    def send_stream_chat_message(self, session_id, message, files=[]):
        messages = self.format_message(message, files)

        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")

        ai_response_stream = self._model_chats[session_id].send_message(messages, stream=True)

        return self.process_ai_response_stream(ai_response_stream)

    def send_stream_single_message(self, message, files=[]):
        messages = self.format_message(message, files)

        ai_response_stream = self._model_instance.generate_content(messages, stream=True)
        return self.process_ai_response_stream(ai_response_stream)

    def process_ai_response_stream(self, responses):
        new_ai_message_args = {}

        try:
            for index, response in enumerate(responses):
                new_ai_message_args = {
                    "index": index,
                    "usage_metadata": str(response.usage_metadata),
                    "candidates": [str(response.candidates) for candidate in response.candidates],
                    "prompt_feedback": str(response.prompt_feedback),
                }

                context_error = ":yellow[Tente reenviar a mensagem novamente]"

                if len(response.candidates) == 0:
                    text_message = f":red[Erro: a resposta gerado pela está vazia. {context_error}]"
                    yield text_message, new_ai_message_args
                    continue

                candidate = response.candidates[0]

                new_ai_message_args.update({
                    "candidate_index": candidate.index,
                    "candidate_content": candidate.content if hasattr(candidate, "content") else None,
                    "candidate_finish_reason": candidate.finish_reason,
                    "candidate_safety_ratings": candidate.safety_ratings,
                    "candidate_function_calls": candidate.function_calls,
                    "candidate_finish_message": candidate.finish_message,
                    "candidate_citation_metadata": candidate.citation_metadata,
                })

                text_message = candidate.text if hasattr(candidate, "text") else ""

                if not hasattr(candidate, "finish_reason") or candidate.finish_reason is None:
                    pass
                elif candidate.finish_reason == FinishReason.STOP:
                    text_message += ""
                elif candidate.finish_reason == FinishReason.MAX_TOKENS:
                    text_message += "...\n\n:yellow[Continue a conversa para mais detalhes]"
                elif candidate.finish_reason == FinishReason.SAFETY:
                    text_message += "\n\n:red[Erro: A resposta contém conteúdo inapropriado.]\n\n"
                    text_message += ":yellow[Tente reformular a mensagem e enviar novamente]"
                elif candidate.finish_reason == FinishReason.RECITATION:
                    text_message += "\n\n:red[Erro: A resposta contém citações não autorizadas.]\n\n"
                    text_message += ":yellow[Tente reformular a mensagem e enviar novamente]"
                yield text_message, new_ai_message_args
        except Exception as e:
            text_message = f":red[Erro ao processar a mensagem: {e}]"
            yield text_message, new_ai_message_args

class LLMGeminiModel1_5Pro(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModel1_0Pro002(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.0-pro-002",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModelExperimental(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-experimental",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )
