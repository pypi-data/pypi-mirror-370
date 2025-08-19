import json

from igbot_base.additional_data import AdditionalData, EMPTY
from igbot_base.base_exception import BaseLlmException
from igbot_base.exception_handler import ExceptionHandler, NoopExceptionHandler
from igbot_base.models import Model
from igbot_base.response_formats import ResponseFormat
from igbot_base.llm import Llm
from igbot_base.llmmemory import LlmMemory
from igbot_base.tool import Tool, ToolCall
from igbot_base.prompt_template import get_logger
from igbot_base.tool_merger_chain import ToolMergerChain
from igbot_base.tool_pre_merger_chain import ToolPreMergerChain

logger = get_logger("application")


class ToolAwareLlmResponseMerger(Llm):

    def __init__(self,
                 name: str,
                 model: Model,
                 temperature: float,
                 tools: list[Tool],
                 tool_merger_chain: ToolMergerChain,
                 tool_pre_merger_chain: ToolPreMergerChain,
                 response_format: ResponseFormat = None,
                 exception_handler: ExceptionHandler = NoopExceptionHandler()):
        super().__init__(name, model, temperature, response_format, exception_handler)
        self.__model = model.value.get_name()
        self.__client = model.value.get_client()
        self.__tools = tools
        self.__tool_merger_chain = tool_merger_chain
        self.__tool_pre_merger_chain = tool_pre_merger_chain

    def _call(self, user_query: str, history: LlmMemory, params: dict, additional_data: AdditionalData = EMPTY):
        history.append_user(user_query)
        response = self.api_call(history)

        if response.choices[0].finish_reason == "tool_calls":
            tools_calls = self.pre_handle_tools(response)
            self.__tool_pre_merger_chain.process(tools_calls)
            response, results = self.handle_tools(response, history)
            self.__tool_merger_chain.process(results)

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
        results = []
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            tool_fn = self.get_tool_function(name)

            try:
                result = tool_fn(**args)
                results.append(result)
            except Exception as e:
                logger.exception("Calling tool %s with args: %s failed at %s: %s",
                                 name, tool_call.function.arguments, self.__str__(), e)
                raise BaseLlmException(f"{name} tool call failed", self, e)

            history.append_tool_response(tool_call.id, result.message)

        return self.api_call(history), results

    def pre_handle_tools(self, response):
        tool_calls = []
        for tool_call in response.choices[0].message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            tool_calls.append(ToolCall(tool_name=name, args=args))

        return tool_calls

    def get_tool_function(self, tool_name):
        for tool in self.__tools:
            if tool_name == tool.get_name():
                return tool.get_function()

        logger.exception(f"Tool %s not found in llm %s",
                         tool_name, self.__str__())
        raise BaseLlmException(f"Tool '{tool_name}' not found in llm {self.__str__()}", self)
