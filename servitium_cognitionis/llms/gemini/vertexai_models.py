from servitium_cognitionis.llms.base import LLMBaseModel

from vertexai import generative_models
from vertexai.generative_models import Part, GenerativeModel, FinishReason

class GeminiVertexAIBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_instance = None
        self._model_chats = {}

    def initialize_model(self, system_instruction=[], temperature=None, max_output_tokens=None):
        self._model_chats = {}
        self._model_instance = GenerativeModel(
            model_name=self.name,
            generation_config={
                "temperature": temperature if temperature else self.temperature,
                "max_output_tokens": max_output_tokens if max_output_tokens else self.max_output_tokens,
            },
            system_instruction=system_instruction,
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        )

    def check_chat_session_exists(self, session_id):
        return session_id in self._model_chats

    def create_chat(self, session_id):
        if self._model_instance is None:
            raise ValueError("Model has not been initialized. Call initialize_model() first")

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = self._model_instance.start_chat(response_validation=False)

    def convert_to_gemini_parts(self, processed_files):
        """
        Converts processed files to Gemini Part objects with filenames.
        """
        gemini_parts = []
        for file in processed_files:
            part = Part.from_data(file.get_content_as_bytes(), mime_type=file.mime_type)

            filename_part = Part.from_text(f"File: `{file.name}`\n")

            gemini_parts.extend([filename_part, part])
        return gemini_parts

    def create_llm_request(self, prompt, system_message, processed_files):
        """
        Creates a complete LLM request with processed files and prompt.
        """
        gemini_system_part = [Part.from_text(system_message), ] if system_message else []
        gemini_file_parts = self.convert_to_gemini_parts(processed_files)
        gemini_prompt_part = [Part.from_text(prompt)]
        return gemini_system_part + gemini_file_parts + gemini_prompt_part

    def send_stream_chat_message(self, session_id, message, system_message=None, files=[]):
        messages = self.create_llm_request(message, system_message, files)

        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")

        ai_response_stream = self._model_chats[session_id].send_message(messages, stream=True)

        return self.process_ai_response_stream(ai_response_stream)

    def send_stream_single_message(self, message, system_message=None, files=[]):
        messages = self.create_llm_request(message, system_message, files)

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
                    # "candidate_safety_ratings": candidate.safety_ratings,
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

class GeminiVertexAIModel1_5Pro(GeminiVertexAIBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class GeminiVertexAIModel1_0Pro002(GeminiVertexAIBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.0-pro-002",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class GeminiVertexAIModelExperimental(GeminiVertexAIBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-experimental",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )
