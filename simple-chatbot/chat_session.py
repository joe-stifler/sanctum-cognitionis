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
    __END_TURN__ = "\n<end_of_turn>\n"

    def __init__(self, model: LLMBaseModel, system="", sqlite_conn=None):
        """
        Initializes the chat state.

        Args:
            model: The language model to use for generating responses.
            system: (Optional) System instructions or bot description.
            sqlite_conn: (Optional) SQLiteConnection object for storing chat history.
        """
        self.model = model
        self.system = system
        self.sqlite_conn = sqlite_conn
        self.session_id = str(uuid.uuid4())  # Generate a unique session ID

        # Create the chat_history table if it doesn't exist
        if self.sqlite_conn:
            self.sqlite_conn.execute(
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

    def add_to_history_as_user(self, message):
        """
        Adds a user message to the history with start/end turn markers.
        """
        if self.sqlite_conn:
            self.sqlite_conn.execute(
                f"INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
                (self.session_id, self.__USER__, message),
            )

    def add_to_history_as_assistant(self, message):
        """
        Adds a assistant response to the history with start/end turn markers.
        """
        if self.sqlite_conn:
            self.sqlite_conn.execute(
                f"INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
                (self.session_id, self.__ASSISTANT__, message),
            )

    def get_history(self):
        """
        Returns the entire chat history as a single string.
        """
        if not self.sqlite_conn:
            return []

        # Fetch history from the database
        chat_history = self.sqlite_conn.query(
            f"SELECT role, message FROM chat_history WHERE session_id = '{self.session_id}'"
        )
        return chat_history

    def get_history_as_turns(self):
        """
        Returns the entire chat history as a single string.
        """
        if not self.sqlite_conn:
            return ""

        # Fetch history from the database
        chat_history = self.get_history()

        turn_history = []
        for role, message in chat_history:
            turn_history.append(
                f"{self.__START_TURN_USER__}{message}{self.__END_TURN__}"
                if role == "user"
                else f"{self.__START_TURN_ASSISTANT__}{message}{self.__END_TURN__}"
            )
        turn_history = "".join(turn_history)
        print(f"Turn history {self.session_id}: \n", turn_history)

        return turn_history

    def get_full_prompt(self):
        """
        Builds the prompt for the language model, including history and system description.
        """
        prompt = self.get_history_as_turns() + self.__START_TURN_ASSISTANT__

        if len(self.system) > 0:
            prompt = self.system + "\n" + prompt
        return prompt

    def send_stream_message(self, message):
        """
        Handles sending a user message and getting a model response.

        Args:
            message: The user's message.

        Returns:
            The model's response.
        """
        self.add_to_history_as_user(message)
        prompt = self.get_full_prompt()
        response = self.model.send_message(prompt)

        # Extract the message content from the generator response. Yield inside
        full_response = ""
        for chunk in response:
            content = chunk["message"]["content"]
            full_response += content
            yield content

        # Add the full processed model response to the chat history
        self.add_to_history_as_assistant(full_response)

        # Return the processed model response
        return full_response
