# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_message import ChatMessage

# module imports from the standard python environment
import uuid


class ChatHistory:
    def __init__(self, session_id, llm_model=None, persona=None):
        self.persona = persona
        self.chat_messages = []
        self.llm_model = llm_model
        self.session_id = session_id
        self.set_system_message = False

    def get_persona(self):
        return self.persona

    def get_llm_model(self):
        return self.llm_model

    def initialize_chat_message(self, llm_model, persona):
        """Initialize the chat and return the system message."""
        assert self.llm_model is None, "Chat already initialized"

        self.persona = persona
        self.llm_model = llm_model

        self.llm_model.initialize_model(
            temperature=self.persona.temperature,
        )
        self.llm_model.create_chat(self.session_id)

    def create_new_message(self, user_message="", user_uploaded_files=None):
        """Create a new chat message and return it."""
        new_chat_message = ChatMessage(
            message_id=str(uuid.uuid4().hex),
            ai_name=self.persona.name,
            user_name="User",
            user_message=user_message,
            user_upload_files=user_uploaded_files,
        )
        self.chat_messages.append(new_chat_message)
        return new_chat_message

    def send_ai_message(self, user_message, user_uploaded_files=None):
        """Send AI response for a given chat message."""
        system_message = None

        if self.set_system_message is False:
            self.set_system_message = True
            system_message = self.persona.present_yourself()

        ai_response_stream = self.llm_model.send_stream_chat_message(
            self.session_id,
            user_message,
            system_message=system_message,
            files=user_uploaded_files,
        )
        new_message = self.create_new_message(user_message, user_uploaded_files)
        new_message.set_ai_message_stream(ai_response_stream)

        return new_message
