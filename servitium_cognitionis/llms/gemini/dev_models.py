from servitium_cognitionis.llms.base import LLMBaseModel

import google.generativeai as genai
from google.ai.generativelanguage import Part, Blob


class GeminiDevBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_instance = None
        self._model_chats = {}

    def initialize_model(self, system_instruction=[], temperature=1.0):
        additional_args = {}
        if len(system_instruction) > 0:
            additional_args = {
                "system_instruction": system_instruction,
            }

        print("Temperature being used: ", temperature)

        self._model_chats = {}
        self._model_instance = genai.GenerativeModel(
            self.name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            ),
            safety_settings={
                "harassment": "block_only_high",
                "hate_speech": "block_only_high",
                "sexual": "block_only_high",
                "dangerous": "block_only_high",
            },
            **additional_args,
        )

    def check_chat_session_exists(self, session_id):
        return session_id in self._model_chats

    def create_chat(self, session_id):
        if self._model_instance is None:
            raise ValueError(
                "Model has not been initialized. Call initialize_model() first"
            )

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = self._model_instance.start_chat()

    def convert_to_gemini_parts(self, processed_files):
        """
        Converts processed files to Gemini Part objects with filenames.
        """
        gemini_parts = []
        for file in processed_files:
            file_content = file.get_content_as_bytes()

            if not isinstance(file_content, list):
                file_content = [
                    file_content,
                ]

            parts = []
            total_parts = len(file_content)

            for idx, file_content_part in enumerate(file_content):
                # Use Part(text...) for text-based files
                if file.media_type == "text":
                    chunk_part = Part(text=f"Part {idx + 1} / {total_parts} of file:\n")
                    parts.extend(
                        [
                            chunk_part,
                            Part(text=file.begin_delimiter_content()),
                            Part(text=file_content_part.decode("utf-8")),
                            Part(text=file.end_delimiter_content()),
                        ]
                    )
                else:
                    chunk_part = Part(text=f"Part {idx + 1} / {total_parts} of file:\n")
                    parts.extend(
                        [
                            chunk_part,
                            Part(text=file.begin_delimiter_content()),
                            Part(
                                inline_data=Blob(
                                    mime_type=file.mime_type,
                                    data=file_content_part,
                                )
                            ),
                            Part(text=file.end_delimiter_content()),
                        ]
                    )

            filename_part = Part(text=file.metadata_header())
            gemini_parts.extend(
                [
                    filename_part,
                ]
                + parts
            )
        return gemini_parts

    def create_llm_request(self, prompt, system_message, processed_files):
        """
        Creates a complete LLM request with processed files and prompt.
        """
        gemini_system_part = (
            [
                Part(text=system_message),
            ]
            if system_message
            else []
        )
        gemini_file_parts = self.convert_to_gemini_parts(processed_files)
        gemini_prompt_part = [Part(text=prompt)]
        return gemini_system_part + gemini_file_parts + gemini_prompt_part

    def send_stream_chat_message(
        self, session_id, message, system_message=None, files=[]
    ):
        messages = self.create_llm_request(message, system_message, files)

        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")

        ai_response_stream = self._model_chats[session_id].send_message(
            messages,
            stream=True,
            request_options={
                "timeout": 60 * 20,
            },
        )

        return self.process_ai_response_stream(session_id, ai_response_stream)

    def send_stream_single_message(self, message, system_message=None, files=[]):
        messages = self.create_llm_request(message, system_message, files)

        ai_response_stream = self._model_instance.generate_content(
            messages, stream=True
        )
        return self.process_ai_response_stream(None, ai_response_stream)

    def process_ai_response_stream(self, session_id, responses):
        new_ai_message_args = {}

        try:
            for chunk in responses:
                text_message = ""
                new_ai_message_args = {}

                if hasattr(chunk, "text"):
                    text_message = chunk.text

                if hasattr(chunk, "prompt_feedback"):
                    new_ai_message_args["prompt_feedback"] = chunk.prompt_feedback

                yield text_message, new_ai_message_args
        except Exception as e:

            if session_id:
                self._model_chats[session_id].rewind()

            text_message = f":red[Erro ao processar a mensagem: {e}]"
            yield text_message, new_ai_message_args


class GeminiDevModelPro1_5(GeminiDevBaseModel):
    def __init__(self, temperature=1.0):
        super().__init__(
            model_name="gemini-1.5-pro",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
        )


class GeminiDevModel1_5_Flash(GeminiDevBaseModel):
    def __init__(self, temperature=1.0):
        super().__init__(
            model_name="gemini-1.5-flash",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
        )
