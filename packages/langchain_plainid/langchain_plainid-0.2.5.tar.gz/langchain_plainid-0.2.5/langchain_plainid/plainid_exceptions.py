import logging
import traceback


class PlainIDException(Exception):
    """Base exception for all PlainID-related errors."""

    def __init__(
        self, message: str, component: str, original_exception: Exception = None
    ):
        self.message = message
        self.component = component
        self.component_stack = [component]
        self.original_exception = original_exception

        # Format a detailed error message
        detailed_msg = f"{message} [component: {component}]"
        if original_exception:
            detailed_msg += f" | Original error: {str(original_exception)}"

        super().__init__(detailed_msg)

        # Log the full traceback for debugging
        if original_exception:
            logging.debug(
                f"PlainID Exception in {component}: {message}\n"
                f"Original exception: {type(original_exception).__name__}: {str(original_exception)}\n"
                f"Original traceback: {''.join(traceback.format_exception(None, original_exception, original_exception.__traceback__))}"
            )
        else:
            logging.debug(
                f"PlainID Exception in {component}: {message}\n"
                f"Traceback: {''.join(traceback.format_stack()[:-1])}"
            )

    def bubble_through(self, component: str):
        """
        Update the component stack when an exception bubbles through a component.

        Args:
            component: The component the exception is bubbling through

        Returns:
            The same exception instance with updated component stack
        """
        self.component_stack.append(component)
        return self


class PlainIDClientException(PlainIDException):
    """Exception raised for errors in the PlainID Client."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDClient", original_exception)


class PlainIDPermissionsException(PlainIDException):
    """Exception raised for errors in permissions processing."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDPermissionsProvider", original_exception)


class PlainIDFilterException(PlainIDException):
    """Exception raised for errors in filter processing."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDFilterProvider", original_exception)


class PlainIDRetrieverException(PlainIDException):
    """Exception raised for errors in the retriever components."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDRetriever", original_exception)


class PlainIDCategorizerException(PlainIDException):
    """Exception raised for errors in the categorizer component."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDCategorizer", original_exception)


class PlainIDAnonymizerException(PlainIDException):
    """Exception raised for errors in the anonymizer component."""

    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message, "PlainIDAnonymizer", original_exception)
