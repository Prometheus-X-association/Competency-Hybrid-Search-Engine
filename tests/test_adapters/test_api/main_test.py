"""Test module for main API application."""

import pytest
from fastapi import FastAPI
from logger import LoggerContract
from pytest_mock import MockerFixture
from sentence_transformers import SentenceTransformer, SparseEncoder

from adapters.api.main import config, lifespan
from adapters.infrastructure.config.contract import ConfigContract
from domain.contracts.db_client import ClientWrapperContract


class TestLifespan:
    """Test suite for lifespan context manager."""

    @pytest.mark.asyncio
    async def test_lifespan_initializes_correctly(self, mocker: MockerFixture) -> None:
        """Test that lifespan correctly initializes configuration and logger."""
        test_app = FastAPI()

        # Setup mocks
        mock_logger = mocker.Mock(spec=LoggerContract)
        mock_logger_class = mocker.patch(
            "adapters.api.main.LoguruLogger",
            return_value=mock_logger,
        )

        mock_model = mocker.Mock(spec=SentenceTransformer)
        mock_load_model = mocker.patch(
            "adapters.api.main.HuggingfaceEmbeddingService.load_sentence_embeddings_model",
            return_value=mock_model,
        )

        mock_sparse_model = mocker.Mock(spec=SparseEncoder)
        mock_load_sparse = mocker.patch(
            "adapters.api.main.HuggingfaceSparseEmbeddingService.load_sparse_encoding_model",
            return_value=mock_sparse_model,
        )

        mock_client = mocker.Mock(spec=ClientWrapperContract)
        mock_client.create_db_collection_if_not_exists.return_value = None
        mock_get_client = mocker.patch(
            "adapters.api.main.get_db_client",
            new_callable=mocker.AsyncMock,
            return_value=mock_client,
        )

        async with lifespan(test_app) as state:
            # Verify state contains expected keys
            assert "config" in state
            assert "logger" in state
            assert "model" in state
            assert "sparse_model" in state

            # Verify types
            assert isinstance(state["config"], ConfigContract)
            assert state["logger"] == mock_logger
            assert state["model"] == mock_model
            assert state["sparse_model"] == mock_sparse_model

            # Verify logger was configured correctly
            mock_logger_class.assert_called_once_with(level=config.get_log_level())

            # Verify startup logging
            mock_logger.info.assert_any_call(
                "Application startup",
                {
                    "log_level": config.get_log_level().name,
                    "environment": config.get_environment().name,
                },
            )
            mock_logger.info.assert_any_call("Application initialized successfully")

            # Verify debug logging
            mock_logger.debug.assert_any_call("Loading embedding model")
            mock_logger.debug.assert_any_call("Loading sparse embedding model")
            mock_logger.debug.assert_any_call(
                "Creating DB collection if it does not exist yet",
            )

            # Verify models were loaded
            mock_load_model.assert_called_once_with(
                model_name=config.get_embedding_model_name(),
            )
            mock_load_sparse.assert_called_once_with(
                model_name=config.get_sparse_embedding_model_name(),
            )

            # Verify DB client operations
            mock_get_client.assert_called_once_with(
                logger=mock_logger,
                config=config,
            )
            mock_client.create_db_collection_if_not_exists.assert_called_once_with(
                collection_name=config.get_db_collection(),
                vector_dimensions=config.get_db_vector_dimensions(),
                vector_distance=config.get_db_vector_distance(),
                dense_vector_name=config.get_dense_vector_name(),
                sparse_vector_name=config.get_sparse_vector_name(),
            )

        # Verify shutdown logging
        mock_logger.info.assert_any_call("Application shutdown")
