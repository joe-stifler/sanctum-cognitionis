from servitium_cognitionis.llms.base import LLMBaseModel

import google.generativeai as genai
from google.ai.generativelanguage import Part, Blob

class GeminiDevBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_instance = None
        self._model_chats = {}

    def initialize_model(self, system_instruction=[], temperature=None, max_output_tokens=None):
        self._model_chats = {}
        self._model_instance = genai.GenerativeModel(
            self.name,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        )

    def check_chat_session_exists(self, session_id):
        return session_id in self._model_chats

    def create_chat(self, session_id):
        if self._model_instance is None:
            raise ValueError("Model has not been initialized. Call initialize_model() first")

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = self._model_instance.start_chat()

    def convert_to_gemini_parts(self, processed_files):
        """
        Converts processed files to Gemini Part objects with filenames.
        """
        gemini_parts = []
        for file in processed_files:
            part = Part(
                inline_data=Blob(
                    mime_type=file.mime_type,
                    data=file.get_content_as_bytes(),
                )
            )

            filename_part = Part(text=f"File: `{file.name}`\n")

            gemini_parts.extend([filename_part, part])
        return gemini_parts

    def create_llm_request(self, prompt, system_message, processed_files):
        """
        Creates a complete LLM request with processed files and prompt.
        """
        gemini_system_part = [Part(text=system_message), ] if system_message else []
        gemini_file_parts = self.convert_to_gemini_parts(processed_files)
        gemini_prompt_part = [Part(text=prompt)]
        return gemini_system_part + gemini_file_parts + gemini_prompt_part

    def send_stream_chat_message(self, session_id, message, system_message=None, files=[]):
        messages = self.create_llm_request(message, system_message, files)

        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")

        ai_response_stream = self._model_chats[session_id].send_message(messages, stream=True)

        return self.process_ai_response_stream(session_id, ai_response_stream)

    def send_stream_single_message(self, message, system_message=None, files=[]):
        messages = self.create_llm_request(message, system_message, files)

        ai_response_stream = self._model_instance.generate_content(messages, stream=True)
        return self.process_ai_response_stream(None, ai_response_stream)

    def process_ai_response_stream(self, session_id, responses):
        new_ai_message_args = {}

        try:
            for chunk in responses:
                text_message = ''
                new_ai_message_args = {}

                if hasattr(chunk, 'text'):
                    text_message = chunk.text

                if hasattr(chunk, 'prompt_feedback'):
                    new_ai_message_args['prompt_feedback'] = chunk.prompt_feedback

                yield text_message, new_ai_message_args
        except Exception as e:
            last_message = ""

            if session_id:
                chat = self._model_chats[session_id]
                last_message = chat.last
                chat.rewind()

            text_message = f":red[Última mensagem: {last_message}\n\nErro ao processar a mensagem: {e}]"
            yield text_message, new_ai_message_args

class GeminiDevModelPro1_0(GeminiDevBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=2048):
        super().__init__(
            model_name="gemini-pro",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 2048)
        )

class GeminiDevModelPro1_0Vision(GeminiDevBaseModel):
    def __init__(self, temperature=0.4, max_output_tokens=4096):
        super().__init__(
            model_name="gemini-pro-vision",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 4096)
        )

class GeminiDevModelPro1_5(GeminiDevBaseModel):
    def __init__(self, temperature=0.4, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.5-pro-latest",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )
