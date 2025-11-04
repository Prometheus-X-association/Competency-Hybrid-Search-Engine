"""Test module for entity API schemas."""

import pytest
from pydantic import ValidationError

from adapters.api.entity.schemas import (
    CreateEntityRequest,
    EntityResponse,
    UpdateEntityRequest,
)
from domain.types.competency import Competency
from domain.types.identifier import Identifier


class TestCreateEntityRequest:
    """Test class for CreateEntityRequest."""

    def test_create_entity_request_valid(self, sample_competency: Competency) -> None:
        """Test valid CreateEntityRequest creation."""
        request = CreateEntityRequest(competency=sample_competency)

        assert request.competency == sample_competency

    def test_create_entity_request_missing_competency(self) -> None:
        """Test CreateEntityRequest with missing competency."""
        with pytest.raises(ValidationError):
            CreateEntityRequest()


class TestUpdateEntityRequest:
    """Test class for UpdateEntityRequest."""

    def test_update_entity_request_valid(self, sample_competency: Competency) -> None:
        """Test valid UpdateEntityRequest creation."""
        request = UpdateEntityRequest(competency=sample_competency)

        assert request.competency == sample_competency

    def test_update_entity_request_missing_competency(self) -> None:
        """Test UpdateEntityRequest with missing competency."""
        with pytest.raises(ValidationError):
            UpdateEntityRequest()


class TestEntityResponse:
    """Test class for EntityResponse."""

    def test_entity_response_valid(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test valid EntityResponse creation."""
        response = EntityResponse(
            identifier=sample_identifier,
            competency=sample_competency,
        )

        assert response.identifier == sample_identifier
        assert response.competency == sample_competency

    def test_entity_response_missing_fields(
        self,
        sample_identifier: Identifier,
        sample_competency: Competency,
    ) -> None:
        """Test EntityResponse with missing fields."""
        # Missing identifier
        with pytest.raises(ValidationError):
            EntityResponse(competency=sample_competency)

        # Missing competency
        with pytest.raises(ValidationError):
            EntityResponse(identifier=sample_identifier)

    def test_entity_response_invalid_uuid(self, sample_competency: Competency) -> None:
        """Test EntityResponse with invalid UUID."""
        with pytest.raises(ValidationError):
            EntityResponse(identifier="invalid-uuid", competency=sample_competency)
