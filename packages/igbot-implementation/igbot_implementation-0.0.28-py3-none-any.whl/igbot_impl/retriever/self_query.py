from igbot_base.base_exception import BaseRetrieverException
from langchain.retrievers import SelfQueryRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.vectorstores import VectorStore

from igbot_base.retriever import Retriever, RetrieverResponse
from igbot_base.prompt_template import get_logger

logger = get_logger("application")


class SelfQuery(Retriever):

    def __init__(
            self,
            vectorstore: VectorStore,
            document_content_description: str,
            model: BaseLanguageModel,
            metadata_field_info):
        super().__init__()
        self.__retriever = SelfQueryRetriever.from_llm(model, vectorstore, document_content_description, metadata_field_info,
                                           enable_limit=False, use_original_query=True)

    def get_relevant_data(self, query: str):
        try:
            return RetrieverResponse(self.__retriever.invoke(input=query))
        except Exception as e:
            logger.exception("Exception occurred at %s for query: %s: %s", self.describe(), query, e)
            raise BaseRetrieverException(f"Exception occurred at {self.describe()} for query: {query}", self, e)

    def describe(self):
        return "SelfQuery()"
