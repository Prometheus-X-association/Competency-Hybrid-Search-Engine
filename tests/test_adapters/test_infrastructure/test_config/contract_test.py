"""Test module for configuration contract."""

from abc import ABCMeta

import pytest

from adapters.infrastructure.config.contract import ConfigContract


class TestConfigContract:
    """Test class for ConfigContract."""

    def test_config_contract_is_abstract(self) -> None:
        """Test that ConfigContract is an abstract class."""
        assert isinstance(ConfigContract, ABCMeta)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            ConfigContract()

    def test_config_contract_abstract_methods(self) -> None:
        """Test that ConfigContract has all required abstract methods."""
        expected_methods = [
            "get_db_method",
            "get_db_host",
            "get_db_port",
            "get_db_url",
            "get_db_api_key",
            "get_db_collection",
            "get_db_vector_distance",
            "get_db_vector_dimensions",
            "get_dense_vector_name",
            "get_sparse_vector_name",
            "get_embedding_method",
            "get_embedding_model_name",
            "get_embedding_vector_dimensions",
            "get_sparse_embedding_model_name",
        ]

        abstract_methods = ConfigContract.__abstractmethods__

        for method in expected_methods:
            assert method in abstract_methods, f"Method {method} should be abstract"

    def test_config_contract_inheritance(self) -> None:
        """Test that ConfigContract properly inherits from CoreConfigContract."""
        from configcore import ConfigContract as CoreConfigContract

        assert issubclass(ConfigContract, CoreConfigContract)

    def test_concrete_implementation_requirement(self) -> None:
        """Test that concrete implementations must implement all abstract methods."""

        # Create a partial implementation missing some methods
        class PartialConfig(ConfigContract):
            def get_db_method(self) -> str:
                return "qdrant"

            def get_db_host(self) -> str:
                return "localhost"

            # Missing other required methods

        # Should not be able to instantiate incomplete implementation
        with pytest.raises(TypeError):
            PartialConfig()

    def test_complete_implementation(self) -> None:  # noqa: C901
        """Test that a complete implementation can be instantiated."""

        class CompleteConfig(ConfigContract):
            def get_db_method(self) -> str:
                return "qdrant"

            def get_db_host(self) -> str:
                return "localhost"

            def get_db_port(self) -> int:
                return 6333

            def get_db_url(self) -> str:
                return "http://localhost:6333"

            def get_db_api_key(self) -> str | None:
                return None

            def get_db_collection(self) -> str:
                return "test"

            def get_db_vector_distance(self) -> str:
                return "Cosine"

            def get_db_vector_dimensions(self) -> int:
                return 1024

            def get_dense_vector_name(self) -> str:
                return "dense"

            def get_sparse_vector_name(self) -> str:
                return "sparse"

            def get_embedding_method(self) -> str:
                return "hf"

            def get_embedding_model_name(self) -> str:
                return "test-model"

            def get_embedding_vector_dimensions(self) -> int:
                return 768

            def get_sparse_embedding_model_name(self) -> str:
                return "test-sparse-model"

            # Required by CoreConfigContract
            def get_environment(self) -> str:
                return "test"

            def get_log_level(self) -> str:
                return "DEBUG"

        # Should be able to instantiate complete implementation
        config = CompleteConfig()

        # Test some methods work
        assert config.get_db_method() == "qdrant"
        assert config.get_db_host() == "localhost"
        assert config.get_db_port() == 6333
        assert config.get_db_api_key() is None
