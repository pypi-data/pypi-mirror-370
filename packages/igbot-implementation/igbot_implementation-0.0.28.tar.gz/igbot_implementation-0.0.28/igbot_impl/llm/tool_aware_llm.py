import json

from igbot_base.additional_data import AdditionalData, EMPTY
from igbot_base.base_exception import BaseLlmException
from igbot_base.exception_handler import ExceptionHandler, NoopExceptionHandler
from igbot_base.models import Model
from igbot_base.response_formats import ResponseFormat
from igbot_base.llm import Llm
from igbot_base.llmmemory import LlmMemory
from igbot_base.tool import Tool
from igbot_base.prompt_template import get_logger

logger = get_logger("application")


class ToolAwareLlm(Llm):

    def __init__(self,
                 name: str,
                 model: Model,
                 temperature: float,
                 tools: list[Tool],
                 response_format: ResponseFormat = None,
                 exception_handler: ExceptionHandler = NoopExceptionHandler()):
        super().__init__(name, model, temperature, response_format, exception_handler)
        self.__model = model.value.get_name()
        self.__client = model.value.get_client()
        self.__tools = tools

    def _call(self, user_query: str, history: LlmMemory, params: dict, additional_data: AdditionalData = EMPTY):
        history.append_user(user_query)
        response = self.api_call(history)

        if response.choices[0].finish_reason == "tool_calls":
            response = self.handle_tools(response, history)

        llm_response = response.choices[0].message.content
        history.append_assistant(llm_response)

        return llm_response

    def _add_llm_message(self, llm_message: str, history: LlmMemory, params: dict) -> str:
        return self._call("Inny Asystent AI napisał: " + llm_message, history, params)

    def api_call(self, history):
        messages = history.retrieve()
        response = self.__client.chat.completions.create(
            model=self.__model,
            messages=messages,
            tools=[tool.get_definition() for tool in self.__tools],
            **super().get_additional_llm_args()
        )
        return response

    def handle_tools(self, response, history):
        history.append_tool_request(response.choices[0].message)
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            tool_fn = self.get_tool_function(name)

            try:
                result = tool_fn(**args)
            except Exception as e:
                logger.exception("Calling tool %s with args: %s failed at %s: %s",
                                 name, tool_call.function.arguments, self.__str__(), e)
                raise BaseLlmException(f"{name} tool call failed", self, e)

            history.append_tool_response(tool_call.id, result)

        return self.api_call(history)

    def get_tool_function(self, tool_name):
        for tool in self.__tools:
            if tool_name == tool.get_name():
                return tool.get_function()

        logger.exception(f"Tool %s not found in llm %s",
                         tool_name, self.__str__())
        raise BaseLlmException(f"Tool '{tool_name}' not found in llm {self.__str__()}", self)
