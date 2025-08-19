from igbot_base.base_exception import BaseRetrieverException
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.retrievers import BaseRetriever

from igbot_base.retriever import Retriever, RetrieverResponse
from igbot_base.prompt_template import get_logger

logger = get_logger("application")


class MultiQuery(Retriever):

    def __init__(
            self,
            retriever: BaseRetriever,
            model: BaseLanguageModel):
        super().__init__()
        self.__retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=model)

    def get_relevant_data(self, query: str):
        try:
            return RetrieverResponse(self.__retriever.invoke(input=query))
        except Exception as e:
            logger.exception("Exception occurred at %s for query: %s: %s", self.describe(), query, e)
            raise BaseRetrieverException(f"Exception occurred at {self.describe()} for query: {query}", self, e)

    def describe(self):
        return "MultiQuery()"
