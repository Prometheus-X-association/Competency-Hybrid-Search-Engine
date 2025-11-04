from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from adapters.exceptions import (
    AdapterError,
    CollectionCreationError,
    DBAdapterError,
    DBConnectionError,
    EmbeddingAdapterError,
    EncodingError,
    ModelLoadingError,
    RepositoryError,
)
from domain.exceptions import (
    DomainError,
    EmbeddingError,
    EntityNotFoundError,
    ValidationError,
)


class ExceptionHandler:
    """Class to handle exceptions in FastAPI.

    This class provides a mechanism to map known exceptions to HTTP status codes
    and to handle unexpected exceptions globally.
    It configures the FastAPI application to use specific exception handlers
    for known exceptions and a catch-all handler for any other exceptions.
    """

    def __init__(self) -> None:
        """Initialize the ExceptionHandler."""
        self.error_mapping: dict[type[Exception], int] = {
            ValidationError: status.HTTP_400_BAD_REQUEST,
            EntityNotFoundError: status.HTTP_404_NOT_FOUND,
            EmbeddingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            EncodingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ModelLoadingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DBConnectionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            CollectionCreationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            RepositoryError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            EmbeddingAdapterError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DBAdapterError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            AdapterError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    def configure(self, app: FastAPI) -> None:
        """Configures the FastAPI application with exception handlers.

        This method registers exception handlers for known exceptions defined in
        `self.error_mapping`. It also adds a global exception handler for any
        unexpected exceptions that may occur during request processing.

        Args:
            app (FastAPI): The FastAPI application instance.
        """
        for exc in self.error_mapping:
            app.add_exception_handler(exc, self.known_exception_handler)

        app.add_exception_handler(Exception, self.global_exception_handler)

    async def known_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handles known exceptions and returns appropriate HTTP responses.

        This method checks the type of the exception and maps it to a specific
        HTTP status code defined in `self.error_mapping`. It logs the exception
        with the request's logger and returns a JSON response containing the
        error message and the corresponding status code.

        Args:
            request (Request): The FastAPI request object, which contains the logger.
            exc (Exception): The exception that was raised during request processing.

        Returns:
            JSONResponse: A JSON response with the error details,
                and the appropriate HTTP status code.
        """
        status_code = self.error_mapping.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        content = {"detail": str(exc)}
        request.state.logger.exception(
            "HTTP Error",
            exc,
            {"status_code": status_code},
        )
        return JSONResponse(status_code=status_code, content=content)

    async def global_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handles unexpected exceptions and returns a generic HTTP 500 response.

        This method is called when an exception occurs that is not explicitly handled
        by the known exception handlers. It logs the exception with the request's logger
        and returns a generic HTTP 500 response.

        Args:
            request (Request): The FastAPI request object, which contains the logger.
            exc (Exception): The exception that was raised during request processing.

        Returns:
            JSONResponse: A JSON response with the error details,
                and a generic HTTP 500 status code.
        """
        content = {"detail": "An error occurred."}
        request.state.logger.exception("Unhandled internal error", exc, {})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content,
        )
