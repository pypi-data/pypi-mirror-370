import time
import math
from igbot_base.llmmemory import LlmMemory
from igbot_base.models import Model
from igbot_base.tokenizer import BaseTokenizer
from openai.types.chat import ChatCompletionMessage

from igbot_impl.igbot_impl.memory.chat_history import BasicInMemoryChatHistory


class RollingDeleteInMemoryChatHistory(BasicInMemoryChatHistory):

    def __init__(self, system_prompt: str, model: Model):
        super().__init__(system_prompt)
        self.__max_token_length_threshold = math.floor(model.value.get_max_tokens() * 0.80)
        self.__result_token_length_threshold = math.floor(model.value.get_max_tokens() * 0.60)
        self.__model = model

    def append_assistant(self, content: str):
        super().append_assistant(content)
        self._trim_messages()

    def append_user(self, content: str):
        super().append_user(content)
        self._trim_messages()

    def append_tool_request(self, message):
        super().append_tool_request(message)

    def append_tool_response(self, tool_call_id: str, content: str):
        super().append_tool_response(tool_call_id, content)

    def _trim_messages(self):
        if self.get_current_token_count(self.__model) < self.__max_token_length_threshold:
            return

        trimmed = self._chat_history.copy()

        def remove_oldest_tool_call_pair():
            """
            Delete first tool call. Deletes tool request and all corresponsing responses
            :return: True if deleted message. False if message was not a tool
            """
            if len(trimmed) < 2:
                return True
            i = 1  # first non system message
            if (trimmed[i]["role"] == "assistant" and "tool_calls" in trimmed[i]
                    or trimmed[i]["role"] == "tool" and "tool_call_id" in trimmed[i]):
                tools_call_count = 0
                for j in range(i + 1, len(trimmed) - i):
                    if trimmed[j]['role'] == 'tool':
                        tools_call_count += 1
                    else:
                        break
                del trimmed[i:i + tools_call_count + 1]
                return True
            return False

        def remove_oldest_non_tool_message():
            """
            Delete first non system user/assistant message
            :return: True if deleted message. False if message was tool
            """
            if len(trimmed) < 2:
                return True
            msg = trimmed[1]
            if msg["role"] in {"user", "assistant"} and "tool_calls" not in msg:
                del trimmed[1]
                return True
            return False

        while self._count_tokens_from_messages(trimmed, self.__model) > self.__result_token_length_threshold:
            if not remove_oldest_tool_call_pair():
                if not remove_oldest_non_tool_message():
                    continue  # nothing else to remove

        self._chat_history = trimmed

    def get_current_token_count(self, model: Model):
        return self._count_tokens_from_messages(self._chat_history, model)

    def _count_tokens_from_messages(self, messages: list, model: Model):
        tokens_per_message = 4
        num_tokens = 0

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if value is not None:
                    num_tokens += model.value.get_tokenizer().count_tokens(value)
        num_tokens += 3
        return num_tokens

    def describe(self):
        return (
            f"RollingDeleteInMemoryChatHistory(size={len(self._chat_history)}, last_updated={self.__last_appended_at},"
            f" last_snapshot_at{self.__snapshot_at_index})")
