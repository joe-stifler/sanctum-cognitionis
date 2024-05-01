from servitium_cognitionis.llms.base import LLMBaseModel

import time
from langchain_core.messages import HumanMessage, AIMessage

class LLMMockBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._model_chats = {}
        self._model_initialized = False

    def initialize_model(self, system_instruction=[]):
        self._model_initialized = True

    def create_chat(self, session_id):
        if self._model_initialized is False:
            raise ValueError("Model has not been initialized. Call initialize_model() first")

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = []

    def send_stream_chat_message(self, session_id, message):
        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")
        
        if len(self._model_chats[session_id]) == 0:
            message = f"Olá! Eu sou um modelo de linguagem de exemplo. O que você gostaria de conversar comigo?"

        self._model_chats[session_id].append(HumanMessage(message))

        def process_message(message_chunks):
            for message in message_chunks:
                self._model_chats[session_id].append(AIMessage(message))
                time.sleep(0.2)

                yield message, {}

        # break 'message' in chunks of 20 chars
        chunked_message = [message[i:i + 20] for i in range(0, len(message), 20)]

        return process_message(chunked_message)


class LLMMockModel(LLMMockBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="mock_model-1.0",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )
