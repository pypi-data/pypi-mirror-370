import logging
from typing import (
    Any,
    List,
    Optional,
    TypeVar,
)

from langchain.retrievers import SelfQueryRetriever
from langchain_core.documents import Document
from langchain_core.runnables import Runnable
from langchain_core.structured_query import (
    StructuredQuery,
)
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, Field, model_validator

from .plainid_default_query_translator import PlainIDDefaultQueryTranslator
from .plainid_exceptions import PlainIDRetrieverException
from .plainid_filter_provider import PlainIDFilterProvider

# Module logger
logger = logging.getLogger(__name__)

# Type variable for the vector store
VST = TypeVar("VST", bound="VectorStore")


class PlainIDRetriever(SelfQueryRetriever, BaseModel):
    vectorstore: VectorStore = Field(description="Vector store to search")
    filter_provider: PlainIDFilterProvider = Field(
        description="Filter provider for queries"
    )
    query_constructor: Optional[Runnable[dict, StructuredQuery]] = Field(
        default=None, alias="llm_chain"
    )
    k: int = Field(default=4, description="Number of documents to return")

    def __init__(self, **data):
        super().__init__(**data)

    @model_validator(mode="before")
    @classmethod
    def validate_translator(cls, values: dict) -> Any:
        try:
            values = SelfQueryRetriever.validate_translator(values)
        except Exception as e:
            logger.debug(f"Using default query translator due to: {str(e)}")
            values["structured_query_translator"] = PlainIDDefaultQueryTranslator()

        return values

    def _get_relevant_documents(
        self, query: str, *, run_manager=None
    ) -> List[Document]:
        """
        Get documents relevant to the query.

        Args:
                query: String to find relevant documents for
                run_manager: Optional run manager for callbacks

        Returns:
                List of relevant documents

        Raises:
                PlainIDRetrieverException: If there was an error retrieving documents
        """
        try:
            logger.info("Getting relevant documents for query: %s", query)

            filter = self.filter_provider.get_filter()

            structured_query = StructuredQuery(query=query, filter=filter, limit=self.k)
            new_query, search_kwargs = super()._prepare_query(query, structured_query)
            logger.info(
                f"new query: {new_query}, using filter: {search_kwargs.get('filter', None)}"
            )
            docs = self._get_docs_with_query(new_query, search_kwargs)
            logger.info("Found %d relevant documents", len(docs))
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query}': {str(e)}")
            raise PlainIDRetrieverException(
                f"Failed to retrieve documents for query: {query}", e
            )
