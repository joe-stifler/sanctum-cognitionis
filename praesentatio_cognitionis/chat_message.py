import os
import hmac
import time
import uuid
import logging
import datetime
import vertexai
import traceback
import google.auth
import pandas as pd
import streamlit as st
from pathlib import Path
from tempfile import NamedTemporaryFile
from streamlit_pdf_viewer import pdf_viewer
from streamlit_feedback import streamlit_feedback
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_extras.stylable_container import stylable_container

class ChatMessage:
    def __init__(self, message_id, ai_name, user_name, user_message, user_upload_files=None):
        self._ai_messages = []
        self.ai_name = ai_name
        self.user_name = user_name
        self._feedback_value = None
        self._message_id = message_id
        self._ai_messages_stream = None
        self._user_message = user_message
        self._timestamp = datetime.datetime.now()
        self._user_uploaded_files = user_upload_files

    @property
    def message_id(self):
        return self._message_id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def feedback_value(self):
        return self._feedback_value

    @feedback_value.setter
    def feedback_value(self, value):
        self._feedback_value = value

    @property
    def user_message(self):
        return self._user_message

    @property
    def user_uploaded_files(self):
        return self._user_uploaded_files

    @property
    def ai_messages(self):
        return [ai_message for ai_message, _ in self._ai_messages]

    @property
    def ai_extra_args(self):
        return [args for _, args in self._ai_messages]

    def add_ai_message(self, ai_message, **kwargs):
        self._ai_messages.append((ai_message, kwargs))

    def set_ai_message_stream(self, ai_message_stream):
        self._ai_messages_stream = ai_message_stream

    def process_ai_messages(self):
        if self._ai_messages_stream:
            for ai_message_chunk, ai_message_args_chunk in self._ai_messages_stream:
                self.add_ai_message(ai_message_chunk, **ai_message_args_chunk)
                yield ai_message_chunk
