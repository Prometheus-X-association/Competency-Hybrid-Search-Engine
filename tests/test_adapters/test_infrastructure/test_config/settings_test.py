"""Test module for configuration settings."""

import pytest
from pytest_mock import MockerFixture

from adapters.infrastructure.config.settings import Settings


class TestSettings:
    """Test class for Settings configuration."""

    def test_default_values(self, mocker: MockerFixture) -> None:
        """Test that Settings has correct default values."""
        mocker.patch.dict("os.environ", {}, clear=True)
        settings = Settings(_env_file=None)

        assert settings.get_db_method() == "qdrant"
        assert settings.get_db_host() == "qdrant"
        assert settings.get_db_port() == 6333
        assert settings.get_db_url() == "http://qdrant:6333"
        assert settings.get_db_api_key() is None
        assert settings.get_db_collection() == "entities"
        assert settings.get_db_vector_distance() == "Cosine"
        assert settings.get_db_vector_dimensions() == 1024
        assert settings.get_dense_vector_name() == "dense"
        assert settings.get_sparse_vector_name() == "sparse"
        assert settings.get_embedding_method() == "hf"
        assert settings.get_embedding_model_name() == "Qwen/Qwen3-Embedding-0.6B"
        assert settings.get_embedding_vector_dimensions() == 1024
        assert (
            settings.get_sparse_embedding_model_name()
            == "opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1"
        )

    def test_direct_field_access(self, mocker: MockerFixture) -> None:
        """Test direct access to Settings fields."""
        mocker.patch.dict("os.environ", {}, clear=True)
        settings = Settings(_env_file=None)

        assert settings.db_method == "qdrant"
        assert settings.db_qdrant_host == "qdrant"
        assert settings.db_qdrant_port == 6333
        assert settings.db_qdrant_url == "http://qdrant:6333"
        assert settings.db_qdrant_api_key is None
        assert settings.db_qdrant_collection == "entities"
        assert settings.db_qdrant_vector_distance == "Cosine"
        assert settings.db_qdrant_vector_dimensions == 1024
        assert settings.db_qdrant_dense_vector_name == "dense"
        assert settings.db_qdrant_sparse_vector_name == "sparse"
        assert settings.embedding_method == "hf"
        assert settings.embedding_hf_model_name == "Qwen/Qwen3-Embedding-0.6B"
        assert settings.embedding_hf_vector_dimensions == 1024
        assert (
            settings.sparse_embedding_model_name
            == "opensearch-project/opensearch-neural-sparse-encoding-multilingual-v1"
        )

    def test_custom_values_via_init(self) -> None:
        """Test Settings with custom values via initialization."""
        custom_settings = Settings(
            db_method="qdrant",
            db_qdrant_host="localhost",
            db_qdrant_port=6334,
            db_qdrant_url="http://localhost:6334",
            db_qdrant_api_key="test-api-key",
            db_qdrant_collection="test-collection",
            db_qdrant_vector_distance="Dot",
            db_qdrant_vector_dimensions=768,
            db_qdrant_dense_vector_name="custom_dense",
            db_qdrant_sparse_vector_name="custom_sparse",
            embedding_method="hf",
            embedding_hf_model_name="test-model",
            embedding_hf_vector_dimensions=768,
            sparse_embedding_model_name="test-sparse-model",
        )

        assert custom_settings.get_db_method() == "qdrant"
        assert custom_settings.get_db_host() == "localhost"
        assert custom_settings.get_db_port() == 6334
        assert custom_settings.get_db_url() == "http://localhost:6334"
        assert custom_settings.get_db_api_key() == "test-api-key"
        assert custom_settings.get_db_collection() == "test-collection"
        assert custom_settings.get_db_vector_distance() == "Dot"
        assert custom_settings.get_db_vector_dimensions() == 768
        assert custom_settings.get_dense_vector_name() == "custom_dense"
        assert custom_settings.get_sparse_vector_name() == "custom_sparse"
        assert custom_settings.get_embedding_method() == "hf"
        assert custom_settings.get_embedding_model_name() == "test-model"
        assert custom_settings.get_embedding_vector_dimensions() == 768
        assert custom_settings.get_sparse_embedding_model_name() == "test-sparse-model"

    def test_environment_variables(self, mocker: MockerFixture) -> None:
        """Test Settings loading from environment variables."""
        mocker.patch.dict(
            "os.environ",
            {
                "DB_METHOD": "qdrant",
                "DB_QDRANT_HOST": "env-host",
                "DB_QDRANT_PORT": "6335",
                "DB_QDRANT_URL": "http://env-host:6335",
                "DB_QDRANT_API_KEY": "env-api-key",
                "DB_QDRANT_COLLECTION": "env-collection",
                "DB_QDRANT_VECTOR_DISTANCE": "Euclid",
                "DB_QDRANT_VECTOR_DIMENSIONS": "512",
                "DB_QDRANT_DENSE_VECTOR_NAME": "env-dense",
                "DB_QDRANT_SPARSE_VECTOR_NAME": "env-sparse",
                "EMBEDDING_METHOD": "hf",
                "EMBEDDING_HF_MODEL_NAME": "env-model",
                "EMBEDDING_HF_VECTOR_DIMENSIONS": "512",
                "SPARSE_EMBEDDING_MODEL_NAME": "env-sparse-model",
            },
        )
        settings = Settings()

        assert settings.get_db_method() == "qdrant"
        assert settings.get_db_host() == "env-host"
        assert settings.get_db_port() == 6335
        assert settings.get_db_url() == "http://env-host:6335"
        assert settings.get_db_api_key() == "env-api-key"
        assert settings.get_db_collection() == "env-collection"
        assert settings.get_db_vector_distance() == "Euclid"
        assert settings.get_db_vector_dimensions() == 512
        assert settings.get_dense_vector_name() == "env-dense"
        assert settings.get_sparse_vector_name() == "env-sparse"
        assert settings.get_embedding_method() == "hf"
        assert settings.get_embedding_model_name() == "env-model"
        assert settings.get_embedding_vector_dimensions() == 512
        assert settings.get_sparse_embedding_model_name() == "env-sparse-model"

    def test_method_consistency(self) -> None:
        """Test that getter methods return the same values as direct field access."""
        settings = Settings(
            db_method="qdrant",
            db_qdrant_host="test-host",
            db_qdrant_port=1234,
            db_qdrant_url="http://test:1234",
            db_qdrant_api_key="test-key",
            db_qdrant_collection="test-coll",
            db_qdrant_vector_distance="Manhattan",
            db_qdrant_vector_dimensions=256,
            db_qdrant_dense_vector_name="test-dense",
            db_qdrant_sparse_vector_name="test-sparse",
            embedding_method="hf",
            embedding_hf_model_name="test-embed",
            embedding_hf_vector_dimensions=256,
            sparse_embedding_model_name="test-sparse",
        )

        # Test that getter methods match field values
        assert settings.get_db_method() == settings.db_method
        assert settings.get_db_host() == settings.db_qdrant_host
        assert settings.get_db_port() == settings.db_qdrant_port
        assert settings.get_db_url() == settings.db_qdrant_url
        assert settings.get_db_api_key() == settings.db_qdrant_api_key
        assert settings.get_db_collection() == settings.db_qdrant_collection
        assert settings.get_db_vector_distance() == settings.db_qdrant_vector_distance
        assert (
            settings.get_db_vector_dimensions() == settings.db_qdrant_vector_dimensions
        )
        assert settings.get_dense_vector_name() == settings.db_qdrant_dense_vector_name
        assert (
            settings.get_sparse_vector_name() == settings.db_qdrant_sparse_vector_name
        )
        assert settings.get_embedding_method() == settings.embedding_method
        assert settings.get_embedding_model_name() == settings.embedding_hf_model_name
        assert (
            settings.get_embedding_vector_dimensions()
            == settings.embedding_hf_vector_dimensions
        )
        assert (
            settings.get_sparse_embedding_model_name()
            == settings.sparse_embedding_model_name
        )

    def test_api_key_none_handling(self) -> None:
        """Test that API key can be None and is handled properly."""
        settings = Settings(db_qdrant_api_key=None)
        assert settings.get_db_api_key() is None

        settings_with_key = Settings(db_qdrant_api_key="some-key")
        assert settings_with_key.get_db_api_key() == "some-key"

    @pytest.mark.parametrize("port", ["6333", 6333, 6333.0])
    def test_port_type_conversion(self, port: str | float) -> None:
        """Test that port values are properly converted to integers."""
        settings = Settings(db_qdrant_port=port)
        assert isinstance(settings.get_db_port(), int)
        assert settings.get_db_port() == 6333

    @pytest.mark.parametrize("dim", ["1024", 1024, 1024.0])
    def test_dimensions_type_conversion(self, dim: str | float) -> None:
        """Test that dimension values are properly converted to integers."""
        settings = Settings(
            db_qdrant_vector_dimensions=dim,
            embedding_hf_vector_dimensions=dim,
        )

        assert isinstance(settings.get_db_vector_dimensions(), int)
        assert isinstance(settings.get_embedding_vector_dimensions(), int)
        assert settings.get_db_vector_dimensions() == 1024
        assert settings.get_embedding_vector_dimensions() == 1024

    def test_vector_dimension_mismatch_validation(self) -> None:
        """Test that dimension mismatch raises ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Vector dimension mismatch") as exc_info:
            Settings(
                db_qdrant_vector_dimensions=512,
                embedding_hf_vector_dimensions=1024,
            )

        error_message = str(exc_info.value)
        assert "Vector dimension mismatch" in error_message
        assert "1024" in error_message
        assert "512" in error_message

    def test_vector_dimension_match_validation_success(self) -> None:
        """Test that matching dimensions pass validation."""
        # Should not raise any exception
        settings = Settings(
            db_qdrant_vector_dimensions=768,
            embedding_hf_vector_dimensions=768,
        )
        assert settings.get_db_vector_dimensions() == 768
        assert settings.get_embedding_vector_dimensions() == 768

    def test_vector_dimension_default_match(self, mocker: MockerFixture) -> None:
        """Test that default dimensions match and pass validation."""
        mocker.patch.dict("os.environ", {}, clear=True)
        settings = Settings(_env_file=None)
        # Default values should match
        assert settings.get_db_vector_dimensions() == 1024
        assert settings.get_embedding_vector_dimensions() == 1024
