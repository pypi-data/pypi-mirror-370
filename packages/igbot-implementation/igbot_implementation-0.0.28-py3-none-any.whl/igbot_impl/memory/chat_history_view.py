import time

from igbot_base.base_exception import BaseMemoryException
from igbot_base.llmmemory import LlmMemory


class ChatHistoryView(LlmMemory):

    def __init__(self, history_slice: list[dict[str, str]]):
        self._chat_history = history_slice

    def retrieve(self):
        return self._chat_history.copy()

    def append_user(self, content: str):
        """Add query for error handling"""
        self._chat_history.append({'role': 'user', 'content': content})

    def append_assistant(self, content: str):
        """Get response for error handling"""
        self._chat_history.append({'role': 'assistant', 'content': content})

    def append_system(self, content: str):
        """
        appends system message at the start of history
        """
        self._chat_history = [{'role': 'system', 'content': content}] + self._chat_history

    def append_tool_request(self, message):
        pass

    def append_tool_response(self, tool_call_id: str, content: str):
        pass

    def clean_conversation(self):
        self._chat_history = []

    def delete_last_user_message(self):
        pass

    def delete_last_tool_message(self):
        pass

    def delete_last_assistant_message(self):
        pass

    def remove_last_entry(self, role) -> None:
        pass

    def revert_to_snapshot(self):
        pass

    def set_snapshot(self):
        pass

    def describe(self):
        return f"ChatHistoryView(size={len(self._chat_history)}"

    def slice(self, messages_number, skip_tool=True) -> LlmMemory:
        raise BaseMemoryException("Can't slice already sliced memory", self)
