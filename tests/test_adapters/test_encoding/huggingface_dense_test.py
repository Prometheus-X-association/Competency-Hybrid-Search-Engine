"""Test module for HuggingfaceEmbeddingService."""

import pytest
from logger import LoggerContract
from numpy import array as np_array
from pytest_mock import MockerFixture
from sentence_transformers import SentenceTransformer

from adapters.encoding.huggingface_dense import HuggingfaceEmbeddingService
from adapters.exceptions import EncodingError, ModelLoadingError
from domain.types.vectors import DenseVector


class TestHuggingfaceEmbeddingService:
    """Test class for HuggingfaceEmbeddingService."""

    @pytest.fixture
    def mock_sentence_transformer(self, mocker: MockerFixture) -> SentenceTransformer:
        """Mock SentenceTransformer fixture."""
        mock_model = mocker.Mock(spec=SentenceTransformer)
        mock_model.encode.return_value = np_array([0.1, 0.2, 0.3, 0.4, 0.5])
        return mock_model

    @pytest.fixture
    def service(
        self,
        mock_sentence_transformer: SentenceTransformer,
        mock_logger: LoggerContract,
    ) -> HuggingfaceEmbeddingService:
        """HuggingfaceEmbeddingService fixture."""
        return HuggingfaceEmbeddingService(
            model=mock_sentence_transformer,
            logger=mock_logger,
        )

    def test_initialization(
        self,
        mock_sentence_transformer: SentenceTransformer,
        mock_logger: LoggerContract,
    ) -> None:
        """Test service initialization."""
        service = HuggingfaceEmbeddingService(
            model=mock_sentence_transformer,
            logger=mock_logger,
        )

        assert service.model == mock_sentence_transformer
        assert service.logger == mock_logger

    def test_encode_success(
        self,
        service: HuggingfaceEmbeddingService,
        mock_sentence_transformer: SentenceTransformer,
        mock_logger: LoggerContract,
    ) -> None:
        """Test successful text encoding."""
        text = "test text"

        result = service.encode(text)

        assert isinstance(result, DenseVector)
        assert result.values == [0.1, 0.2, 0.3, 0.4, 0.5]

        # Verify model was called correctly
        mock_sentence_transformer.encode.assert_called_once_with(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        # Verify logging
        mock_logger.debug.assert_called()

    def test_encode_with_model_not_available(self, mock_logger: LoggerContract) -> None:
        """Test encoding when model is None."""
        service = HuggingfaceEmbeddingService(
            model=None,
            logger=mock_logger,
        )

        with pytest.raises(EncodingError, match="Failed to encode text"):
            service.encode("test text")

    def test_encode_with_encoding_error(
        self,
        mock_sentence_transformer: SentenceTransformer,
        mock_logger: LoggerContract,
    ) -> None:
        """Test encoding when model raises an exception."""
        mock_sentence_transformer.encode.side_effect = RuntimeError("Model error")

        service = HuggingfaceEmbeddingService(
            model=mock_sentence_transformer,
            logger=mock_logger,
        )

        with pytest.raises(EncodingError, match="Failed to encode text"):
            service.encode("test text")

        mock_logger.exception.assert_called()

    def test_load_dense_encoding_model_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test successful model loading."""
        mock_sentence_transformer_class = mocker.patch(
            "adapters.encoding.huggingface_dense.SentenceTransformer",
        )
        mock_model = mocker.Mock(spec=SentenceTransformer)
        mock_sentence_transformer_class.return_value = mock_model

        model_name = "test-model"
        result = HuggingfaceEmbeddingService.load_sentence_embeddings_model(model_name)

        assert result == mock_model
        mock_sentence_transformer_class.assert_called_once_with(model_name)

    def test_load_dense_encoding_model_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test model loading failure."""
        mock_sentence_transformer_class = mocker.patch(
            "adapters.encoding.huggingface_dense.SentenceTransformer",
        )
        mock_sentence_transformer_class.side_effect = RuntimeError(
            "Failed to load model",
        )

        model_name = "invalid-model"

        with pytest.raises(ModelLoadingError, match="Failed to load model"):
            HuggingfaceEmbeddingService.load_sentence_embeddings_model(model_name)
