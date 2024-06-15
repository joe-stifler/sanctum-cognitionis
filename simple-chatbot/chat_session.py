import uuid
from llm_model import LLMBaseModel
import sqlite3


class ChatSession:
    """
    Manages the conversation history for a turn-based chatbot
    Follows the turn-based conversation guidelines for the Gemma family of models documented at https://ai.google.dev/gemma/docs/formatting
    """

    __USER__ = "user"
    __ASSISTANT__ = "assistant"

    __START_TURN_USER__ = f"<start_of_turn>{__USER__}\n"
    __START_TURN_ASSISTANT__ = f"<start_of_turn>{__ASSISTANT__}\n"
    __END_TURN_USER__ = f"<end_of_turn>\n"
    __END_TURN_ASSISTANT__ = f"<end_of_turn>\n"

    def __init__(self, system="", connection=None):
        """
        Initializes the chat state.

        Args:
            system: (Optional) System instructions or bot description.
            connection: (Optional) SQLiteConnection object for storing chat history.
        """
        self.model = None
        self.system = system
        self.connection = connection
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID

        # Create the chat_history table if it doesn't exist
        if self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def is_model_initialized(self):
        """
        Checks if the language model is initialized.

        Returns:
            True if the model is initialized, False otherwise.
        """
        return self.model is not None

    def update_model(self, model: LLMBaseModel):
        """
        Updates the language model used by the chat session.

        Args:
            model: The new language model to use.
        """
        self.model = model

    def add_to_history_as_user(self, message):
        """
        Adds a user message to the history with start/end turn markers.
        """
        if self.connection:
            self.connection.execute(
                "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
                (self.session_id, self.__USER__, message),
            )

    def add_to_history_as_assistant(self, message):
        """
        Adds a assistant response to the history with start/end turn markers.
        """
        if self.connection:
            self.connection.execute(
                "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
                (self.session_id, self.__ASSISTANT__, message),
            )

    def get_history(self):
        """
        Returns the entire chat history as a single string.
        """
        if not self.connection:
            return []

        # Fetch history from the database
        chat_history = self.connection.query(
            f"SELECT role, message FROM chat_history WHERE session_id = '{self.session_id}'"
        )
        return chat_history

    def get_history_as_turns(self):
        """
        Returns the entire chat history as a single string.
        """
        if not self.connection:
            return ""

        # Fetch history from the database
        chat_history = self.get_history()

        turn_history = []

        for role, message in chat_history:
            if role == self.__USER__:
                turn_history.append(
                    f"{self.__START_TURN_USER__}{message}{self.__END_TURN_USER__}"
                )
            else:
                turn_history.append(
                    f"{self.__START_TURN_ASSISTANT__}{message}{self.__END_TURN_ASSISTANT__}"
                )

        str_turn_history = "".join(turn_history)

        return "Chat history for your context:" + str_turn_history

    def send_stream_message(self, message):
        """
        Handles sending a user message and getting a model response.

        Args:
            message: The user's message.

        Returns:
            The model's response.
        """
        self.add_to_history_as_user(message)

        # Check if the model is initialized
        if self.model is None:
            # raise and exception with message asking to initilize the model
            raise ValueError("Model not initialized. Please update the model.")

        prompt = self.get_history_as_turns() + "\nNew user message: " + message
        response_stream = self.model.send_stream_message(prompt)

        # Extract the message content from the generator response. Yield inside
        full_response = ""
        for chunk_content in response_stream:
            full_response += chunk_content
            yield chunk_content

        # Add the full processed model response to the chat history
        self.add_to_history_as_assistant(full_response)
