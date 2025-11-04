"""Test module for HuggingfaceSparseEmbeddingService."""

import pytest
from logger import LoggerContract
from numpy import array as np_array
from pytest_mock import MockerFixture
from sentence_transformers import SparseEncoder
from torch import Tensor

from adapters.encoding.huggingface_sparse import HuggingfaceSparseEmbeddingService
from adapters.exceptions import EncodingError, ModelLoadingError
from domain.types.vectors import SparseVector


class TestHuggingfaceSparseEmbeddingService:
    """Test class for HuggingfaceSparseEmbeddingService."""

    @pytest.fixture
    def mock_sparse_encoder(self, mocker: MockerFixture) -> SparseEncoder:
        """Mock SparseEncoder fixture."""
        mock_encoder = mocker.Mock(spec=SparseEncoder)

        # Create a mock sparse tensor
        mock_tensor = mocker.Mock(spec=Tensor)
        mock_tensor.coalesce.return_value = mock_tensor
        mock_tensor.indices.return_value.cpu.return_value.numpy.return_value = np_array(
            [[0, 2, 4]],
        )
        mock_tensor.values.return_value.cpu.return_value.numpy.return_value = np_array(
            [0.1, 0.3, 0.5],
        )
        mock_tensor.shape = (3,)

        mock_encoder.encode.return_value = mock_tensor
        return mock_encoder

    @pytest.fixture
    def service(
        self,
        mock_sparse_encoder: SparseEncoder,
        mock_logger: LoggerContract,
    ) -> HuggingfaceSparseEmbeddingService:
        """HuggingfaceSparseEmbeddingService fixture."""
        return HuggingfaceSparseEmbeddingService(
            model=mock_sparse_encoder,
            logger=mock_logger,
        )

    def test_initialization(
        self,
        mock_sparse_encoder: SparseEncoder,
        mock_logger: LoggerContract,
    ) -> None:
        """Test service initialization."""
        service = HuggingfaceSparseEmbeddingService(
            model=mock_sparse_encoder,
            logger=mock_logger,
        )

        assert service.model == mock_sparse_encoder
        assert service.logger == mock_logger

    def test_encode_success(
        self,
        service: HuggingfaceSparseEmbeddingService,
        mock_sparse_encoder: SparseEncoder,
        mock_logger: LoggerContract,
    ) -> None:
        """Test successful text encoding."""
        text = "test text"

        result = service.encode(text)

        assert isinstance(result, SparseVector)
        assert result.indices == [0, 2, 4]
        assert result.values == [0.1, 0.3, 0.5]

        # Verify model was called correctly
        mock_sparse_encoder.encode.assert_called_once_with(
            text,
            convert_to_tensor=True,
            convert_to_sparse_tensor=True,
        )

        # Verify logging
        mock_logger.debug.assert_called()

    def test_encode_with_model_not_available(self, mock_logger: LoggerContract) -> None:
        """Test encoding when model is None."""
        service = HuggingfaceSparseEmbeddingService(
            model=None,
            logger=mock_logger,
        )

        with pytest.raises(EncodingError, match="Sparse model not available"):
            service.encode("test text")

    def test_encode_with_encoding_error(
        self,
        mock_sparse_encoder: SparseEncoder,
        mock_logger: LoggerContract,
    ) -> None:
        """Test encoding when model raises an exception."""
        mock_sparse_encoder.encode.side_effect = RuntimeError("Model error")

        service = HuggingfaceSparseEmbeddingService(
            model=mock_sparse_encoder,
            logger=mock_logger,
        )

        with pytest.raises(EncodingError, match="Failed to encode sparse text"):
            service.encode("test text")

        mock_logger.exception.assert_called()

    def test_encode_without_coalesce(
        self,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test encoding with tensor that doesn't have coalesce method."""
        mock_encoder = mocker.Mock(spec=SparseEncoder)

        # Create a mock sparse tensor without coalesce
        mock_tensor = mocker.Mock(
            spec=["indices", "values", "shape"],
        )  # Only has indices, values, shape - no coalesce
        mock_tensor.indices.return_value.cpu.return_value.numpy.return_value = np_array(
            [0, 1, 3],
        )
        mock_tensor.values.return_value.cpu.return_value.numpy.return_value = np_array(
            [0.2, 0.4, 0.6],
        )
        mock_tensor.shape = (4,)

        mock_encoder.encode.return_value = mock_tensor

        service = HuggingfaceSparseEmbeddingService(
            model=mock_encoder,
            logger=mock_logger,
        )

        result = service.encode("test text")

        assert isinstance(result, SparseVector)
        assert result.indices == [0, 1, 3]
        assert result.values == [0.2, 0.4, 0.6]

        # Verify encode was called with correct parameters
        mock_encoder.encode.assert_called_once_with(
            "test text",
            convert_to_tensor=True,
            convert_to_sparse_tensor=True,
        )

    def test_encode_with_multidimensional_indices(
        self,
        mock_logger: LoggerContract,
        mocker: MockerFixture,
    ) -> None:
        """Test encoding with multidimensional indices array."""
        mock_encoder = mocker.Mock(spec=SparseEncoder)

        mock_tensor = mocker.Mock(spec=Tensor)
        mock_tensor.coalesce.return_value = mock_tensor
        # Return 2D indices array
        mock_tensor.indices.return_value.cpu.return_value.numpy.return_value = np_array(
            [[0, 1, 2]],
        )
        mock_tensor.values.return_value.cpu.return_value.numpy.return_value = np_array(
            [0.1, 0.2, 0.3],
        )
        mock_tensor.shape = (3,)

        mock_encoder.encode.return_value = mock_tensor

        service = HuggingfaceSparseEmbeddingService(
            model=mock_encoder,
            logger=mock_logger,
        )

        result = service.encode("test text")

        assert isinstance(result, SparseVector)
        assert result.indices == [0, 1, 2]  # Should be flattened
        assert result.values == [0.1, 0.2, 0.3]

    def test_load_sparse_encoding_model_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test successful model loading."""
        mock_sparse_encoder_class = mocker.patch(
            "adapters.encoding.huggingface_sparse.SparseEncoder",
        )
        mock_model = mocker.Mock(spec=SparseEncoder)
        mock_sparse_encoder_class.return_value = mock_model

        model_name = "test-model"
        result = HuggingfaceSparseEmbeddingService.load_sparse_encoding_model(
            model_name,
        )

        assert result == mock_model
        mock_sparse_encoder_class.assert_called_once_with(model_name)

    def test_load_sparse_encoding_model_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test model loading failure."""
        mock_sparse_encoder_class = mocker.patch(
            "adapters.encoding.huggingface_sparse.SparseEncoder",
        )
        mock_sparse_encoder_class.side_effect = RuntimeError(
            "Failed to load sparse model",
        )

        model_name = "invalid-model"

        with pytest.raises(ModelLoadingError, match="Failed to load sparse model"):
            HuggingfaceSparseEmbeddingService.load_sparse_encoding_model(model_name)
