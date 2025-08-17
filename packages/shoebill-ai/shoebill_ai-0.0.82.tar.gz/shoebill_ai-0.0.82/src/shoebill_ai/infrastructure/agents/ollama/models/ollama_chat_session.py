from typing import List

from .ollama_chat_message import OllamaChatMessage


class OllamaChatSession:
    def __init__(self, session_id: str, messages: List[OllamaChatMessage]):
        self.session_id = session_id
        self.messages = messages

    def add_message(self, message: OllamaChatMessage):
        self.messages.append(message)
