from servitium_cognitionis.llms.base import LLMBaseModel

import time
from langchain_core.messages import HumanMessage, AIMessage

class LLMMockBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._model_chats = {}
        self._model_initialized = False

    def initialize_model(self, system_instruction=[], temperature=None, max_output_tokens=None):
        self._model_initialized = True
        self._model_chats = {}

    def process_message(self, session_id, message_chunks):
        for message in message_chunks:
            if session_id:
                self._model_chats[session_id].append(AIMessage(message))
            time.sleep(0.01)
            yield message, {}

    def check_chat_session_exists(self, session_id):
        return session_id in self._model_chats

    def create_chat(self, session_id):
        if self._model_initialized is False:
            raise ValueError("Model has not been initialized. Call initialize_model() first")

        if session_id in self._model_chats:
            raise ValueError("Chat session already exists. Call end_chat() first")

        self._model_chats[session_id] = []

    def send_stream_chat_message(self, session_id, message, files=[]):
        files = ['sending uploaded file: ' + key + '\n' for key, _ in files]

        if session_id not in self._model_chats:
            raise ValueError("Chat session does not exist. Call create_chat() first")

        if len(self._model_chats[session_id]) == 0:
            message = "Olá! Eu sou o Zoid Mock! Prazer em conhecê-lo. O que você gostaria de saber hoje?"

        self._model_chats[session_id].append(HumanMessage(message))

        # break 'message' in chunks of 20 chars
        chunked_message = files + [message[i:i + 20] for i in range(0, len(message), 20)]

        return self.process_message(session_id, chunked_message)

    def send_stream_single_message(self, message, files=[]):
        files = ['sending uploaded file: ' + key + '\n' for key, _ in files]

        chunked_message = files + [message[i:i + 20] for i in range(0, len(message), 20)]
        return self.process_message(None, chunked_message)

class LLMMockModel(LLMMockBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="mock_model-1.0",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )
