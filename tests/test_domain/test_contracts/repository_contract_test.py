"""Test module for RepositoryContract."""

from abc import ABC
from collections.abc import Sequence

import pytest

from domain.contracts.repository import RepositoryContract
from domain.types.entity import Entity
from domain.types.filters import DomainFilter
from domain.types.identifier import Identifier
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import DenseVector, SparseVector


class TestRepositoryContract:
    """Test class for RepositoryContract."""

    def test_repository_contract_is_abstract(self) -> None:
        """Test that RepositoryContract is abstract."""
        assert issubclass(RepositoryContract, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            RepositoryContract()

    def test_repository_contract_abstract_methods(self) -> None:
        """Test that all required methods are abstract."""

        # Create a concrete implementation that doesn't implement all methods
        class IncompleteRepository(RepositoryContract):
            def create_entity(self, model: CreateEntityModel) -> Entity:
                pass

        # Should not be able to instantiate without implementing all abstract methods
        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_repository_contract_concrete_implementation(
        self,
        sample_entity: Entity,
    ) -> None:
        """Test concrete implementation of RepositoryContract."""

        class TestRepository(RepositoryContract):
            def create_entity(self, model: CreateEntityModel) -> Entity:
                return sample_entity

            def get_entity(self, identifier: Identifier) -> Entity | None:
                return sample_entity

            def update_entity(self, model: UpdateEntityModel) -> Entity:
                return sample_entity

            def delete_entity(self, identifier: Identifier) -> None:
                return

            def search_by_vector_and_filters(
                self,
                vector: DenseVector | SparseVector,
                filters: Sequence[DomainFilter],
                top: int,
                vector_name: str = "dense",
            ) -> Sequence[SearchResult]:
                # Simple implementation for testing
                sample_score = 0.8
                return [SearchResult(entity=sample_entity, score=sample_score)]

            def search_hybrid_by_vectors_and_filters(
                self,
                dense_vector: DenseVector,
                sparse_vector: SparseVector,
                filters: Sequence[DomainFilter],
                top: int,
            ) -> Sequence[SearchResult]:
                return []

        # Should be able to instantiate concrete implementation
        repository = TestRepository()
        assert isinstance(repository, RepositoryContract)
