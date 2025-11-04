"""Test module for search API router."""

from collections.abc import Callable, Generator

import pytest
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.testclient import TestClient
from logger import LoggerContract
from pytest_mock import MockerFixture

from adapters.api.dependencies import get_entity_service
from adapters.api.exception_handler import ExceptionHandler
from adapters.api.search.router import router
from domain.services.entity_service import EntityService
from domain.types.entity import Entity
from domain.types.search_type import SearchType as DomainSearchType
from domain.types.service_models import SearchResult


class TestSearchRouter:
    """Test class for search router endpoints."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create FastAPI app with search router."""
        app = FastAPI()
        app.include_router(router)
        # Configure exception handler
        exception_handler = ExceptionHandler()
        exception_handler.configure(app)
        return app

    @pytest.fixture
    def client(self, app: FastAPI, mock_logger: LoggerContract) -> TestClient:
        """Create test client."""

        # Add mock logger to request state for exception handler
        @app.middleware("http")
        async def add_mock_logger(
            request: Request,
            call_next: Callable[[Request], Response],
        ) -> Response:
            request.state.logger = mock_logger
            return await call_next(request)

        return TestClient(app)

    @pytest.fixture
    def mock_entity_service(
        self,
        app: FastAPI,
        mocker: MockerFixture,
    ) -> Generator[EntityService]:
        """Mock entity service dependency."""
        mock_service = mocker.Mock(spec=EntityService)

        # Create an async mock function to replace the dependency
        async def get_mock_service() -> EntityService:
            return mock_service

        # Override the dependency in the app
        app.dependency_overrides[get_entity_service] = get_mock_service

        yield mock_service

        # Clean up after the test
        app.dependency_overrides.clear()

    @pytest.fixture
    def sample_search_results(self, sample_entity: Entity) -> list[SearchResult]:
        """Create sample search results for testing."""
        return [
            SearchResult(entity=sample_entity, score=0.95),
            SearchResult(entity=sample_entity, score=0.87),
        ]

    def test_search_with_semantic_type(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_search_results: list[SearchResult],
    ) -> None:
        """Test search with semantic search type."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = (
            sample_search_results
        )

        search_request = {
            "text": "programming skills",
            "search_type": "semantic",
            "top": 10,
            "filters": [],
        }

        response = client.post("/search/text", json=search_request)

        assert response.status_code == 200
        response_data = response.json()
        assert "results" in response_data
        assert len(response_data["results"]) == len(sample_search_results)
        assert response_data["results"][0]["score"] == sample_search_results[0].score
        assert (
            response_data["results"][0]["competency"]["title"]
            == sample_search_results[0].entity.competency.title
        )

        # Verify service was called with correct parameters
        mock_entity_service.search_by_text_and_filters_with_type.assert_called_once_with(
            text="programming skills",
            filters=[],
            top=10,
            search_type=DomainSearchType.SEMANTIC,
        )

    def test_search_with_sparse_type(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_search_results: list[SearchResult],
    ) -> None:
        """Test search with sparse search type."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = (
            sample_search_results
        )

        search_request = {
            "text": "programming skills",
            "search_type": "sparse",
            "top": 5,
            "filters": [],
        }

        response = client.post("/search/text", json=search_request)

        assert response.status_code == 200
        response_data = response.json()
        assert "results" in response_data
        assert len(response_data["results"]) == len(sample_search_results)
        assert response_data["results"][0]["score"] == sample_search_results[0].score
        assert (
            response_data["results"][0]["competency"]["title"]
            == sample_search_results[0].entity.competency.title
        )

        # Verify service was called with correct parameters
        mock_entity_service.search_by_text_and_filters_with_type.assert_called_once_with(
            text="programming skills",
            filters=[],
            top=5,
            search_type=DomainSearchType.SPARSE,
        )

    def test_search_with_hybrid_type(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_search_results: list[SearchResult],
    ) -> None:
        """Test search with hybrid search type."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = (
            sample_search_results
        )

        search_request = {
            "text": "programming skills",
            "search_type": "hybrid",
            "top": 5,
            "filters": [],
        }

        response = client.post("/search/text", json=search_request)

        assert response.status_code == 200
        response_data = response.json()
        assert "results" in response_data
        assert len(response_data["results"]) == len(sample_search_results)
        assert response_data["results"][0]["score"] == sample_search_results[0].score
        assert (
            response_data["results"][0]["competency"]["title"]
            == sample_search_results[0].entity.competency.title
        )

        # Verify service was called with correct parameters
        mock_entity_service.search_by_text_and_filters_with_type.assert_called_once_with(
            text="programming skills",
            filters=[],
            top=5,
            search_type=DomainSearchType.HYBRID,
        )

    def test_search_with_filters(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_search_results: list[SearchResult],
    ) -> None:
        """Test search with filters."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = (
            sample_search_results
        )

        search_request = {
            "text": "programming skills",
            "filters": [
                {
                    "field": "competency.type",
                    "operator": "eq",
                    "value": "TECHNICAL",
                },
                {
                    "field": "competency.level",
                    "operator": "eq",
                    "value": "INTERMEDIATE",
                },
            ],
        }

        response = client.post("/search/text", json=search_request)

        assert response.status_code == 200

        # Verify filters were processed
        mock_entity_service.search_by_text_and_filters_with_type.assert_called_once()
        call_args = mock_entity_service.search_by_text_and_filters_with_type.call_args
        filters = call_args[1]["filters"]
        assert len(filters) == 2

    def test_search_empty_results(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test search that returns no results."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = []

        search_request = {
            "text": "programming skills",
        }

        response = client.post("/search/text", json=search_request)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["results"] == []

    def test_search_invalid_request(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test search with invalid request."""
        # Test with completely invalid structure
        invalid_request = {"invalid_field": "value"}

        response = client.post("/search/text", json=invalid_request)

        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with invalid filter structure
        invalid_filter_request = {
            "text": "programming skills",
            "filters": [
                {
                    "field": "competency.type",
                    # Missing 'operator' and 'value'
                },
            ],
        }
        response = client.post("/search/text", json=invalid_filter_request)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with invalid filter structure (not a list)
        invalid_filter_request_type = {
            "text": "programming skills",
            "filters": {
                "field": "competency.type",
                "operator": "eq",
                "value": "TECHNICAL",
            },  # Should be a list
        }
        response = client.post("/search/text", json=invalid_filter_request_type)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with invalid top value
        invalid_top_request = {
            "text": "programming skills",
            "top": 0,  # Invalid, should be >= 1
        }
        response = client.post("/search/text", json=invalid_top_request)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with invalid top value (too high)
        invalid_top_request_high = {
            "text": "programming skills",
            "top": 101,  # Invalid, should be <= 100
        }
        response = client.post("/search/text", json=invalid_top_request_high)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with empty text
        empty_text_request = {
            "text": "",  # Invalid, min_length=1
        }
        response = client.post("/search/text", json=empty_text_request)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with too long text
        too_long_text_request = {
            "text": "a" * 10001,  # Invalid, max_length=10000
        }
        response = client.post("/search/text", json=too_long_text_request)
        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

        # Test with invalid search type
        invalid_request = {"text": "programming skills", "search_type": "INVALID_TYPE"}

        response = client.post("/search/text", json=invalid_request)

        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

    def test_search_missing_required_fields(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test search with missing required fields."""
        incomplete_request = {
            "search_type": "semantic",
            # Missing 'text' field
        }

        response = client.post("/search/text", json=incomplete_request)

        assert response.status_code == 422
        mock_entity_service.search_by_text_and_filters_with_type.assert_not_called()

    def test_search_default_values(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_search_results: list[SearchResult],
    ) -> None:
        """Test search with minimal request using default values."""
        mock_entity_service.search_by_text_and_filters_with_type.return_value = (
            sample_search_results
        )

        minimal_request = {"text": "programming skills"}

        response = client.post("/search/text", json=minimal_request)

        assert response.status_code == 200

        # Check that defaults were used
        mock_entity_service.search_by_text_and_filters_with_type.assert_called_once_with(
            text="programming skills",
            filters=[],  # Default empty list
            top=10,  # Default value
            search_type=DomainSearchType.SEMANTIC,  # Default value
        )
