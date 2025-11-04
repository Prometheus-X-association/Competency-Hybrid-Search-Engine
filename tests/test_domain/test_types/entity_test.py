"""Test module for Entity type."""

from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.identifier import Identifier
from domain.types.vectors import DenseVector, SparseVector


class TestEntity:
    """Test class for Entity."""

    def test_entity_creation_with_all_fields(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test creating an entity with all fields."""
        entity = Entity(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        assert entity.identifier == sample_identifier
        assert entity.competency == sample_competency
        assert entity.dense_vector == sample_dense_vector
        assert entity.sparse_vector == sample_sparse_vector

    def test_entity_creation_without_vectors(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test creating an entity without vectors (optional fields)."""
        entity = Entity(
            identifier=sample_identifier,
            competency=sample_competency,
        )

        assert entity.identifier == sample_identifier
        assert entity.competency == sample_competency
        assert entity.dense_vector is None
        assert entity.sparse_vector is None

    def test_entity_creation_with_none_vectors(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test creating an entity with explicit None vectors."""
        entity = Entity(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=None,
            sparse_vector=None,
        )

        assert entity.identifier == sample_identifier
        assert entity.competency == sample_competency
        assert entity.dense_vector is None
        assert entity.sparse_vector is None

    def test_entity_equality(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_dense_vector: DenseVector,
        sample_sparse_vector: SparseVector,
    ) -> None:
        """Test entity equality comparison."""
        entity1 = Entity(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )
        entity2 = Entity(
            identifier=sample_identifier,
            competency=sample_competency,
            dense_vector=sample_dense_vector,
            sparse_vector=sample_sparse_vector,
        )

        assert entity1.identifier == entity2.identifier
        assert entity1.competency == entity2.competency
        assert entity1.dense_vector == entity2.dense_vector
        assert entity1.sparse_vector == entity2.sparse_vector
