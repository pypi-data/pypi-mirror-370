from igbot_base.base_exception import BaseRetrieverException
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain_core.retrievers import BaseRetriever

from igbot_base.retriever import Retriever, RetrieverResponse
from igbot_base.prompt_template import get_logger

logger = get_logger("application")


class EmbeddingFilter(Retriever):

    def __init__(
            self,
            retriever: BaseRetriever,
            embedding_function,
            similarity_threshold):
        super().__init__()

        embeddings_filter = EmbeddingsFilter(embeddings=embedding_function, similarity_threshold=similarity_threshold)
        self.__retriever = ContextualCompressionRetriever(base_compressor=embeddings_filter,
                                                          base_retriever=retriever)

    def get_relevant_data(self, query: str) -> RetrieverResponse:
        try:
            return RetrieverResponse(self.__retriever.invoke(input=query))
        except Exception as e:
            logger.exception("Exception occurred at %s for query: %s: %s", self.describe(), query, e)
            raise BaseRetrieverException(f"Exception occurred at {self.describe()} for query: {query}", self, e)

    def describe(self):
        return "EmbeddingFilter()"
