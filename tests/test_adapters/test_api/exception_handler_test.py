"""Test module for API exception handler."""

import pytest
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from logger import LoggerContract
from pytest_mock import MockerFixture
from starlette.datastructures import State

from adapters.api.exception_handler import ExceptionHandler
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


class TestExceptionHandler:
    """Test class for ExceptionHandler."""

    @pytest.fixture
    def handler(self) -> ExceptionHandler:
        """Create ExceptionHandler instance."""
        return ExceptionHandler()

    @pytest.fixture
    def mock_request(self, mocker: MockerFixture) -> Request:
        """Create mock request with logger."""
        request = mocker.Mock(spec=Request)
        request.state = mocker.Mock(spec=State)
        request.state.logger = mocker.Mock(spec=LoggerContract)
        return request

    @pytest.fixture
    def mock_app(self, mocker: MockerFixture) -> FastAPI:
        """Create mock FastAPI app."""
        app = mocker.Mock(spec=FastAPI)
        app.add_exception_handler.return_value = None
        return app

    def test_init_error_mapping(self, handler: ExceptionHandler) -> None:
        """Test ExceptionHandler initialization and error mapping."""
        assert isinstance(handler.error_mapping, dict)

        # Check that all expected exceptions are mapped
        expected_exceptions = [
            ValidationError,
            EntityNotFoundError,
            EmbeddingError,
            EncodingError,
            ModelLoadingError,
            DBConnectionError,
            CollectionCreationError,
            RepositoryError,
            EmbeddingAdapterError,
            DBAdapterError,
            AdapterError,
            DomainError,
        ]

        for exc_type in expected_exceptions:
            assert exc_type in handler.error_mapping
            assert isinstance(handler.error_mapping[exc_type], int)

    def test_configure_adds_handlers(
        self,
        handler: ExceptionHandler,
        mock_app: FastAPI,
    ) -> None:
        """Test that configure adds exception handlers to app."""
        handler.configure(mock_app)

        # Check add_exception_handler was called for mapped exceptions + global
        expected_calls = len(handler.error_mapping) + 1  # +1 for global handler
        assert mock_app.add_exception_handler.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_known_exception_handler_error(
        self,
        handler: ExceptionHandler,
        mock_request: Request,
    ) -> None:
        """Test handling ValidationError."""
        for error_class, status_code in handler.error_mapping.items():
            exc = error_class("Invalid input")

            response = await handler.known_exception_handler(mock_request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status_code
            assert response.body == b'{"detail":"Invalid input"}'

        assert mock_request.state.logger.exception.call_count == len(
            handler.error_mapping.keys(),
        )

    @pytest.mark.asyncio
    async def test_known_exception_handler_unknown_exception(
        self,
        handler: ExceptionHandler,
        mock_request: Request,
    ) -> None:
        """Test handling unknown exception type."""

        class UnknownError(Exception):
            pass

        exc = UnknownError("Unknown error")

        response = await handler.known_exception_handler(mock_request, exc)

        # Should default to 500 for unknown exception types
        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body == b'{"detail":"Unknown error"}'
        mock_request.state.logger.exception.assert_called_once()

    @pytest.mark.asyncio
    async def test_global_exception_handler(
        self,
        handler: ExceptionHandler,
        mock_request: Request,
    ) -> None:
        """Test global exception handler."""
        exc = Exception("Unexpected error")

        response = await handler.global_exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.body == b'{"detail":"An error occurred."}'
        mock_request.state.logger.exception.assert_called_once_with(
            "Unhandled internal error",
            exc,
            {},
        )

    @pytest.mark.asyncio
    async def test_global_exception_handler_various_exceptions(
        self,
        handler: ExceptionHandler,
        mock_request: Request,
    ) -> None:
        """Test global exception handler with various exception types."""
        exceptions = [
            Exception("Unexpected error"),
            RuntimeError("Runtime error"),
            ValueError("Value error"),
            KeyError("Key error"),
            TypeError("Type error"),
        ]

        for exc in exceptions:
            response = await handler.global_exception_handler(mock_request, exc)

            assert isinstance(response, JSONResponse)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.body == b'{"detail":"An error occurred."}'

        assert mock_request.state.logger.exception.call_count == len(exceptions)
