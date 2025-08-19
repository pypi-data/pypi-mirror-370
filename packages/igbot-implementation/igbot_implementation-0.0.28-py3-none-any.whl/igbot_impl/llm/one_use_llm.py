from typing import Optional

from igbot_base.additional_data import AdditionalData, EMPTY
from igbot_base.exception_handler import ExceptionHandler, NoopExceptionHandler
from igbot_base.llm import Llm
from igbot_base.llmmemory import LlmMemory
from igbot_base.models import Model
from igbot_base.prompt_template import Prompt


class OneUseLlm(Llm):

    def __init__(self,
                 name: str,
                 model: Model,
                 temperature: float,
                 system_prompt: Prompt,
                 response_format: Optional[dict],
                 exception_handler: ExceptionHandler = NoopExceptionHandler()):
        super().__init__(name, model, temperature, response_format, exception_handler)
        self.__client = self._model.value.get_client()
        self.__system_prompt = system_prompt

    def _call(self, user_query: str, history: LlmMemory, params: dict, additional_data: AdditionalData = EMPTY):
        messages = [
            {"role": "system", "content": self.__system_prompt.parse(params)},
            {"role": "user", "content": user_query}
        ]
        response = self.__client.chat.completions.create(
            model=self._model.value.get_name(),
            messages=messages,
            **super().get_additional_llm_args()
        )
        llm_response = response.choices[0].message.content

        return llm_response

    def _add_llm_message(self, llm_message: str, history: LlmMemory, params: dict) -> str:
        return self._call("Inny Asystent AI napisał: " + llm_message, history, params)
