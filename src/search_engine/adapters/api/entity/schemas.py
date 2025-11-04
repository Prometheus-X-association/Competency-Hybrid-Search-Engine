from uuid import UUID

from pydantic import BaseModel, Field

from domain.types.competency import Competency


class CreateEntityRequest(BaseModel):
    """Model for creating a new entity."""

    competency: Competency = Field(..., description="Competency data of the entity.")


class UpdateEntityRequest(BaseModel):
    """Model for updating an existing entity."""

    competency: Competency = Field(..., description="The updated competency data.")


class EntityResponse(BaseModel):
    """Model for an entity response."""

    identifier: UUID = Field(..., description="UUID of the entity.")
    competency: Competency = Field(..., description="Competency data of the entity.")
