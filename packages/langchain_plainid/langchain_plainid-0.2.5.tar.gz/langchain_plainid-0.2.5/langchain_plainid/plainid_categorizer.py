import logging
from typing import Any, Optional

from langchain_core.runnables import Runnable, RunnableConfig

from .category_classifier_provider import CategoryClassifierProvider
from .plainid_exceptions import PlainIDCategorizerException
from .plainid_permissions_provider import PlainIDPermissionsProvider


class PlainIDCategorizer(Runnable[str, str]):
    def __init__(
        self,
        classifier_provider: CategoryClassifierProvider,
        permissions_provider: PlainIDPermissionsProvider,
        all_categories: Optional[list[str]] = None,
    ):
        self.classifier_provider = classifier_provider
        self.permissions_provider = permissions_provider
        self.all_categories = all_categories or []

    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        try:
            allowed = self.permissions_provider.get_allowed_categories()
            category = self.classifier_provider.classify(
                input, self.all_categories, allowed
            )

            if category is None:
                raise PlainIDCategorizerException(
                    "Failed to classify input into a valid category"
                )

            logging.debug(f"Categorizer result: {category}")
            return category
        except PlainIDCategorizerException:
            # Re-raise categorizer exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            raise PlainIDCategorizerException("Error during categorization", e)

    async def ainvoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> str:
        """Asynchronously process a single string input."""
        import asyncio
        from functools import partial

        # Use run_in_executor to run invoke method in a separate thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, partial(self.invoke, input, config, **kwargs)
        )
