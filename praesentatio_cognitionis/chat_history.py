# module imports from the praesentatio_cognitionis package
from praesentatio_cognitionis.chat_message import ChatMessage

# module imports from the standard python environment
import uuid

class ChatHistory:
    def __init__(self, session_id, llm_model, persona):
        self.persona = persona
        self.chat_messages = []
        self.llm_model = llm_model
        self.session_id = session_id

    def get_persona(self):
        return self.persona

    def maybe_initialize_chat_message(self):
        """Initialize the chat and return the system message."""
        if not self.llm_model.check_chat_session_exists(self.session_id):
            logger.info("Initializing chat")
            self.llm_model.initialize_model(
                temperature=self.persona.creativity_level,
                system_instruction=[
                    self.persona.present_yourself()
                ],
                max_output_tokens=self.persona.speech_conciseness
            )
            self.llm_model.create_chat(self.session_id)

    def create_new_message(self, user_message="", user_uploaded_files=None):
        """Create a new chat message and return it."""
        new_chat_message = ChatMessage(
            message_id=str(uuid.uuid4().hex),
            ai_name=self.persona.name,
            user_name="Usuário",
            user_message=user_message,
            user_upload_files=user_uploaded_files
        )
        self.chat_messages.append(new_chat_message)
        return new_chat_message

    def send_ai_message(self, user_message, user_uploaded_files=None):
        """Send AI response for a given chat message."""
        logger.info("Sending user message:\n\n```text\n%s\n```", user_message)
        self.maybe_initialize_chat_message()

        new_message = self.create_new_message(user_message, user_uploaded_files)
        ai_response_stream = self.llm_model.send_stream_chat_message(
            self.session_id,
            user_message,
            user_uploaded_files
        )
        new_message.set_ai_message_stream(ai_response_stream)

        return new_message
