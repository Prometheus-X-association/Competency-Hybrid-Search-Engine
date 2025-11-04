"""Test module for entity API router."""

from collections.abc import Callable, Generator

import pytest
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.testclient import TestClient
from logger import LoggerContract
from pytest_mock import MockerFixture
from starlette.responses import Response

from adapters.api.dependencies import get_entity_service
from adapters.api.entity.router import router
from adapters.api.exception_handler import ExceptionHandler
from domain.exceptions import EntityNotFoundError
from domain.services.entity_service import EntityService
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.identifier import Identifier


class TestEntityRouter:
    """Test class for entity router endpoints."""

    @pytest.fixture
    def app(self) -> FastAPI:
        """Create FastAPI app with entity router."""
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

    def test_create_entity_success(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_competency: Competency,
        sample_entity: Entity,
    ) -> None:
        """Test successful entity creation."""
        mock_entity_service.create_entity.return_value = sample_entity

        response = client.post(
            "/entities",
            json={"competency": sample_competency.model_dump()},
        )

        assert response.status_code == 201

        json_response = response.json()

        assert "identifier" in json_response
        assert "competency" in json_response
        assert json_response["competency"]["title"] == sample_competency.title

        mock_entity_service.create_entity.assert_called_once_with(
            competency=sample_competency,
            text=sample_competency.indexed_text,
        )

    def test_create_entity_invalid_request(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity creation with invalid request."""
        invalid_data = {"invalid": "data"}

        response = client.post("/entities", json=invalid_data)

        assert response.status_code == 422
        mock_entity_service.create_entity.assert_not_called()

    def test_get_entity_success(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_entity: Entity,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test successful entity retrieval."""
        mock_entity_service.get_entity.return_value = sample_entity

        response = client.get(f"/entities/{sample_identifier}")

        assert response.status_code == 200

        json_response = response.json()

        assert "identifier" in json_response
        assert "competency" in json_response

        assert json_response["identifier"] == str(sample_identifier)
        assert json_response["competency"]["title"] == sample_competency.title

        mock_entity_service.get_entity.assert_called_once_with(
            identifier=sample_identifier,
        )

    def test_get_entity_invalid_request(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity retrieval with invalid request."""
        invalid_identifier = "invalid-uuid"

        response = client.get(f"/entities/{invalid_identifier}")

        assert response.status_code == 422
        mock_entity_service.get_entity.assert_not_called()

    def test_get_entity_not_found(
        self,
        client: TestClient,
        sample_identifier: Identifier,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity retrieval when entity not found."""
        mock_entity_service.get_entity.side_effect = EntityNotFoundError(
            "Entity not found",
        )

        response = client.get(f"/entities/{sample_identifier!s}")

        assert response.status_code == 404
        assert "Entity not found" in response.json()["detail"]
        mock_entity_service.get_entity.assert_called_once_with(
            identifier=sample_identifier,
        )

    def test_update_entity_success(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_competency: Competency,
        sample_entity: Entity,
        sample_identifier: Identifier,
    ) -> None:
        """Test successful entity update."""
        mocked_competency = sample_competency.model_copy()
        mocked_competency.indexed_text = "Advanced Python Programming"
        updated_competency = mocked_competency.model_dump()

        mock_entity_service.update_entity.return_value = sample_entity

        response = client.put(
            f"/entities/{sample_identifier!s}",
            json={"competency": updated_competency},
        )

        assert response.status_code == 200
        assert "identifier" in response.json()

        mock_entity_service.update_entity.assert_called_once_with(
            identifier=sample_identifier,
            competency=mocked_competency,
            text=updated_competency["indexed_text"],
        )

    def test_update_entity_without_indexed_text(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_identifier: Identifier,
        sample_competency: Competency,
        sample_entity: Entity,
    ) -> None:
        """Test entity update without indexed_text."""
        mocked_competency = sample_competency.model_copy()
        mocked_competency.indexed_text = None
        competency_without_indexed_text = mocked_competency.model_dump()

        mock_entity_service.update_entity.return_value = sample_entity

        response = client.put(
            f"/entities/{sample_identifier}",
            json={"competency": competency_without_indexed_text},
        )

        assert response.status_code == 200

        mock_entity_service.update_entity.assert_called_once_with(
            identifier=sample_identifier,
            competency=mocked_competency,
            text=None,
        )

    def test_update_entity_invalid_request(
        self,
        client: TestClient,
        sample_identifier: Identifier,
        sample_competency: Competency,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity update with invalid request."""
        # Invalid body
        invalid_data = {"invalid": "data"}
        response = client.put(f"/entities/{sample_identifier}", json=invalid_data)

        assert response.status_code == 422
        mock_entity_service.update_entity.assert_not_called()

        # Invalid UUID
        invalid_identifier = "invalid-uuid"
        response = client.put(
            f"/entities/{invalid_identifier}",
            json={"competency": sample_competency.model_dump()},
        )

        assert response.status_code == 422
        mock_entity_service.update_entity.assert_not_called()

    def test_delete_entity_success(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
        sample_identifier: Identifier,
    ) -> None:
        """Test successful entity deletion."""
        mock_entity_service.delete_entity.return_value = None

        response = client.delete(f"/entities/{sample_identifier}")

        assert response.status_code == 204
        assert response.content == b""

        mock_entity_service.delete_entity.assert_called_once_with(
            identifier=sample_identifier,
        )

    def test_delete_entity_invalid_request(
        self,
        client: TestClient,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity deletion with invalid request."""
        invalid_identifier = "invalid-uuid"

        response = client.delete(f"/entities/{invalid_identifier}")

        assert response.status_code == 422
        mock_entity_service.delete_entity.assert_not_called()

    def test_delete_entity_not_found(
        self,
        client: TestClient,
        sample_identifier: Identifier,
        mock_entity_service: EntityService,
    ) -> None:
        """Test entity deletion when entity not found."""
        mock_entity_service.delete_entity.side_effect = EntityNotFoundError(
            "Entity not found",
        )

        response = client.delete(f"/entities/{sample_identifier!s}")

        assert response.status_code == 404
        assert "Entity not found" in response.json()["detail"]
        mock_entity_service.delete_entity.assert_called_once_with(
            identifier=sample_identifier,
        )
