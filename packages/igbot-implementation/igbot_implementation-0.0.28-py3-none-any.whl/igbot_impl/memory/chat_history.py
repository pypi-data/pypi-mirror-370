import time

from igbot_base.base_exception import BaseMemoryException
from igbot_base.llmmemory import LlmMemory
from openai.types.chat import ChatCompletionMessage

from igbot_impl.memory.chat_history_view import ChatHistoryView


class BasicInMemoryChatHistory(LlmMemory):

    def __init__(self, system_prompt: str):
        self.__last_appended_at = None
        self.__snapshot_at_index = None
        self._chat_history: list[dict[str, str]] = [{'role': 'system', 'content': system_prompt}]

    def retrieve(self):
        return self._chat_history.copy()

    def append_user(self, content: str):
        self._chat_history.append({'role': 'user', 'content': content})
        self.__last_appended_at = time.time()

    def append_assistant(self, content: str):
        self._chat_history.append({'role': 'assistant', 'content': content})
        self.__last_appended_at = time.time()

    def append_system(self, content: str):
        self._chat_history.append({'role': 'system', 'content': content})
        self.__last_appended_at = time.time()

    def append_tool_request(self, message):
        """
        Appends tool requests transforming ChatCompletionsMessage to dict if necessary
        :param message: some tool call response message
        """
        if isinstance(message, ChatCompletionMessage):
            llm_msg = {
                'role': message.role,
                'content': message.content,
            }

            if hasattr(message, "tool_calls") and message.tool_calls:
                llm_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            self._chat_history.append(llm_msg)

        elif isinstance(message, dict):
            self._chat_history.append(message)

        else:
            raise BaseMemoryException(f"Tried to append history for tool_request with type {type(message)}", self)

        self.__last_appended_at = time.time()

    def append_tool_response(self, tool_call_id: str, content: str):
        self._chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        })
        self.__last_appended_at = time.time()

    def clean_conversation(self):
        self._chat_history = [
            item for item in self._chat_history
            if not (isinstance(item, dict) and item.get("role") == "tool")
               and not isinstance(item, dict)
        ]

    def delete_last_user_message(self):
        self.remove_last_entry("user")

    def delete_last_tool_message(self):
        self.remove_last_entry("tool")

    def delete_last_assistant_message(self):
        self.remove_last_entry("assistant")

    def remove_last_entry(self, role) -> None:
        if role == 'tool':
            tool_index = None
            for i in range(len(self._chat_history) - 1, -1, -1):
                if self._chat_history[i].get("role") == 'assistant' and self._chat_history[i].get("tool_calls"):
                    tool_index = i
                    break
            if tool_index is None:
                return
            del self._chat_history[tool_index]
            while tool_index < len(self._chat_history):
                if self._chat_history[tool_index].get("role") == 'tool':
                    del self._chat_history[tool_index]
                else:
                    break
            return

        for i in range(len(self._chat_history) - 1, -1, -1):
            if self._chat_history[i].get("role") == role:
                del self._chat_history[i]
                break

    def revert_to_snapshot(self):
        self._chat_history = self._chat_history[:self.__snapshot_at_index + 1]

    def set_snapshot(self):
        self.__snapshot_at_index = len(self._chat_history) - 1

    def describe(self):
        return (f"BasicInMemoryChatHistory(size={len(self._chat_history)}, last_updated={self.__last_appended_at},"
                f" last_snapshot_at{self.__snapshot_at_index})")

    def slice(self, messages_number, skip_tool=True) -> LlmMemory:
        sliced = self.retrieve()
        if skip_tool:
            sliced = [
                item for item in sliced
                if not item.get("role") == "tool" and not item.get("tool_calls")
            ]
        return ChatHistoryView(sliced[-messages_number:])
