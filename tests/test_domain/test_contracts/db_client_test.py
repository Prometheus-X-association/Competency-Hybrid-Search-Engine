"""Test module for ClientWrapperContract."""

from abc import ABC
from typing import TypeVar

import pytest

from domain.contracts.db_client import ClientWrapperContract

# Define a test client type for testing
TestClientType = TypeVar("TestClientType")


class MockClient:
    """Mock client for testing purposes."""

    def __init__(self, name: str = "test-client") -> None:
        """Initialize the mock client."""
        self.name = name


class TestClientWrapperContract:
    """Test class for ClientWrapperContract."""

    def test_client_wrapper_contract_is_abstract(self) -> None:
        """Test that ClientWrapperContract is abstract."""
        assert issubclass(ClientWrapperContract, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            ClientWrapperContract()

    def test_client_wrapper_contract_is_generic(self) -> None:
        """Test that ClientWrapperContract is generic."""
        # Test that it's a generic class
        assert hasattr(ClientWrapperContract, "__parameters__")

    def test_client_wrapper_contract_abstract_methods(self) -> None:
        """Test that all required methods are abstract."""

        # Create a concrete implementation that doesn't implement all methods
        class IncompleteClientWrapper(ClientWrapperContract[MockClient]):
            def create_db_collection_if_not_exists(
                self,
                collection_name: str,
                vector_dimensions: int,
                vector_distance: str,
                dense_vector_name: str,
                sparse_vector_name: str,
            ) -> None:
                pass

        # Should not be able to instantiate without implementing all abstract methods
        with pytest.raises(TypeError):
            IncompleteClientWrapper()

        # Create a concrete implementation that doesn't implement all methods
        class IncompleteClientWrapper(ClientWrapperContract[MockClient]):
            def get_client(self) -> MockClient:
                pass

        # Should not be able to instantiate without implementing all abstract methods
        with pytest.raises(TypeError):
            IncompleteClientWrapper()

    def test_client_wrapper_contract_concrete_implementation(self) -> None:
        """Test concrete implementation of ClientWrapperContract."""

        class TestClientWrapper(ClientWrapperContract[MockClient]):
            def create_db_collection_if_not_exists(
                self,
                collection_name: str,
                vector_dimensions: int,
                vector_distance: str,
                dense_vector_name: str,
                sparse_vector_name: str,
            ) -> None:
                return

            def get_client(self) -> MockClient:
                return MockClient()

        # Should be able to instantiate concrete implementation
        wrapper = TestClientWrapper()
        assert isinstance(wrapper, ClientWrapperContract)
        assert isinstance(wrapper, ABC)
