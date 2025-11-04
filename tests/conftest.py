"""This file contains pytest fixtures available to all tests.

Fixtures are functions that pytest runs before tests to set up preconditions.
pytest automatically discovers this file and makes fixtures available
to all test modules without needing to import them.
"""

from uuid import uuid4

import pytest
from logger import LoggerContract
from pytest_mock import MockerFixture

from adapters.infrastructure.config.contract import ConfigContract
from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.contracts.repository import RepositoryContract
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.identifier import Identifier
from domain.types.service_models import (
    SearchResult,
)
from domain.types.vectors import DenseVector, SparseVector


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> LoggerContract:
    """Mock logger fixture."""
    return mocker.Mock(spec=LoggerContract)


@pytest.fixture
def mock_repository(mocker: MockerFixture) -> RepositoryContract:
    """Mock repository fixture."""
    return mocker.Mock(spec=RepositoryContract)


@pytest.fixture
def mock_embedding_service(mocker: MockerFixture) -> EmbeddingServiceContract:
    """Mock embedding service fixture."""
    return mocker.Mock(spec=EmbeddingServiceContract)


@pytest.fixture
def mock_sparse_embedding_service(
    mocker: MockerFixture,
) -> SparseEmbeddingServiceContract:
    """Mock sparse embedding service fixture."""
    return mocker.Mock(spec=SparseEmbeddingServiceContract)


@pytest.fixture
def mock_config(mocker: MockerFixture) -> ConfigContract:
    """Mock config fixture."""
    config = mocker.Mock(spec=ConfigContract)
    config.get_db_url.return_value = "http://localhost:6333"
    config.get_db_api_key.return_value = "test_api_key"
    config.get_db_collection.return_value = "test_collection"
    config.get_db_vector_distance.return_value = "Cosine"
    config.get_db_vector_dimensions.return_value = 5
    config.get_dense_vector_name.return_value = "dense"
    config.get_sparse_vector_name.return_value = "sparse"
    return config


@pytest.fixture
def sample_identifier() -> Identifier:
    """Sample identifier fixture."""
    return uuid4()


@pytest.fixture
def sample_competency() -> Competency:
    """Sample competency fixture."""
    return Competency(
        code="code",
        lang="fr",
        type="skill",
        provider="esco",
        title="Title / Label",
        description="Preferred human-readable label of the item.",
        url=None,
        category=None,
        keywords=None,
        indexed_text=None,
        metadata=None,
    )


@pytest.fixture
def sample_dense_vector() -> DenseVector:
    """Sample dense vector fixture."""
    return DenseVector(values=[0.1, 0.2, 0.3, 0.4, 0.5])


@pytest.fixture
def sample_sparse_vector() -> SparseVector:
    """Sample sparse vector fixture."""
    return SparseVector(indices=[0, 2, 4], values=[0.1, 0.3, 0.5])


@pytest.fixture
def sample_entity(
    sample_identifier: Identifier,
    sample_competency: Competency,
    sample_dense_vector: DenseVector,
    sample_sparse_vector: SparseVector,
) -> Entity:
    """Sample entity fixture."""
    return Entity(
        identifier=sample_identifier,
        competency=sample_competency,
        dense_vector=sample_dense_vector,
        sparse_vector=sample_sparse_vector,
    )


@pytest.fixture
def sample_search_result(sample_entity: Entity) -> SearchResult:
    """Sample search result fixture."""
    return SearchResult(entity=sample_entity, score=0.95)
