import time
from igbot_base.llmmemory import LlmMemory


class NoMemory(LlmMemory):

    def describe(self):
        return "NoMemory()"

    def retrieve(self):
        return []

    def append_user(self, content: str):
        pass

    def append_assistant(self, content: str):
        pass

    def append_system(self, content: str):
        pass

    def append_tool_request(self, message):
        pass

    def append_tool_response(self, tool_call_id: str, content: str):
        pass

    def clean_conversation(self):
        pass

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

    def slice(self, messages_number, skip_tool=True):
        pass
