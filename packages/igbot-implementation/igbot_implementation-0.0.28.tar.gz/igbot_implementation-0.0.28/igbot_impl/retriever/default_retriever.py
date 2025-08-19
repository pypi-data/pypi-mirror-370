from igbot_base.base_exception import BaseRetrieverException
from langchain_core.retrievers import BaseRetriever

from igbot_base.retriever import Retriever
from igbot_base.retriever import RetrieverResponse
from igbot_base.logging_adapter import get_logger

logger = get_logger("application")


class DefaultRetriever(Retriever):

    def __init__(
            self,
            retriever: BaseRetriever):
        super().__init__()
        self.__retriever = retriever

    def get_relevant_data(self, query: str) -> RetrieverResponse:
        try:
            return RetrieverResponse(self.__retriever.invoke(input=query))
        except Exception as e:
            logger.exception("Exception occurred at %s for query: %s: %s", self.describe(), query, e)
            raise BaseRetrieverException(f"Exception occurred at {self.describe()} for query: {query}", self, e)

    def describe(self):
        return "DefaultRetriever()"
