"""Test module for service models."""

from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.identifier import Identifier
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import DenseVector, SparseVector


class TestSearchResult:
    """Test class for SearchResult."""

    def test_search_result_creation(self, sample_entity: Entity) -> None:
        """Test creating a SearchResult."""
        score = 0.95

        search_result = SearchResult(entity=sample_entity, score=score)

        assert search_result.entity == sample_entity
        assert search_result.score == score

    def test_search_result_with_different_scores(self, sample_entity: Entity) -> None:
        """Test SearchResult with different score values."""
        scores = [0.0, 0.5, 0.95, 1.0, -0.1, 1.5]

        for score in scores:
            search_result = SearchResult(entity=sample_entity, score=score)
            assert search_result.score == score

    def test_search_result_equality(self, sample_entity: Entity) -> None:
        """Test SearchResult equality."""
        score = 0.95

        result1 = SearchResult(entity=sample_entity, score=score)
        result2 = SearchResult(entity=sample_entity, score=score)

        assert result1.score == result2.score
        assert result1.entity.identifier == result2.entity.identifier


class TestCreateEntityModel:
    """Test class for CreateEntityModel."""

    def test_create_entity_model_creation(
        self,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test creating a CreateEntityModel."""
        model = CreateEntityModel(
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        assert model.competency == sample_competency
        assert model.dense_vector == sample_dense_vector
        assert model.sparse_vector == sample_sparse_vector

    def test_create_entity_model_vector_types(
        self,
        sample_competency: Competency,
    ) -> None:
        """Test CreateEntityModel with different vector types."""
        dense_vectors = [
            DenseVector(values=[1.0, 2.0, 3.0]),
            DenseVector(values=[0.1, 0.2, 0.3]),
            DenseVector(values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]),
        ]

        sparse_vectors = [
            SparseVector(indices=[0, 1], values=[1.0, 2.0]),
            SparseVector(indices=[0, 2, 4], values=[0.1, 0.3, 0.5]),
            SparseVector(indices=[1, 3, 5, 7, 9], values=[1.0, 2.0, 3.0, 4.0, 5.0]),
        ]

        for dense_vec, sparse_vec in zip(dense_vectors, sparse_vectors, strict=False):
            model = CreateEntityModel(
                competency=sample_competency,
                dense_vector=dense_vec,
                sparse_vector=sparse_vec,
            )
            assert model.dense_vector == dense_vec
            assert model.sparse_vector == sparse_vec


class TestUpdateEntityModel:
    """Test class for UpdateEntityModel."""

    def test_update_entity_model_creation(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test creating an UpdateEntityModel."""
        model = UpdateEntityModel(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        assert model.identifier == sample_identifier
        assert model.competency == sample_competency
        assert model.dense_vector == sample_dense_vector
        assert model.sparse_vector == sample_sparse_vector

    def test_update_entity_model_equality(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test UpdateEntityModel equality."""
        model1 = UpdateEntityModel(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        model2 = UpdateEntityModel(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        # Test individual components
        assert model1.identifier == model2.identifier
        assert model1.competency == model2.competency
        assert model1.dense_vector == model2.dense_vector
        assert model1.sparse_vector == model2.sparse_vector
