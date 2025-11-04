from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from adapters.api.dependencies import get_entity_service
from adapters.api.entity.schemas import (
    CreateEntityRequest,
    EntityResponse,
    UpdateEntityRequest,
)
from adapters.api.mapper import ApiEntityMapper
from domain.services.entity_service import EntityService
from domain.types.identifier import Identifier

router = APIRouter(prefix="/entities", tags=["Entities"])


@router.post(
    "",
    summary="Create a new entity",
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_none=True,
)
async def create_entity(
    req: CreateEntityRequest,
    service: Annotated[EntityService, Depends(get_entity_service)],
) -> EntityResponse:
    """Create a new entity with the provided competency data and text to encode.

    This endpoint allows you to create a new entity in the system.
    The `competency` should contain the necessary data for the entity.
    It returns the created entity as a response.

    Args:
        req (CreateEntityRequest): The request object containing the entity data.
        service (EntityService): The entity service dependency.

    Returns:
        EntityResponse: The response object containing the created entity.
    """
    entity = service.create_entity(
        competency=req.competency,
        text=req.competency.indexed_text,
    )
    return ApiEntityMapper.domain_to_adapter(entity)


@router.get(
    "/{entity_id}",
    summary="Retrieve an entity by ID",
    response_model_exclude_none=True,
)
async def get_entity(
    entity_id: Annotated[Identifier, Path(...)],
    service: Annotated[EntityService, Depends(get_entity_service)],
) -> EntityResponse:
    """Retrieve an entity by its ID.

    This endpoint allows you to fetch an entity using its unique identifier.
    The `entity_id` should be provided in the path, and it returns the entity details.

    Args:
        entity_id (Identifier): The unique identifier of the entity.
        service (EntityService): The entity service dependency.

    Returns:
        EntityResponse: The response object containing the entity details.
    """
    entity = service.get_entity(identifier=entity_id)
    return ApiEntityMapper.domain_to_adapter(entity)


@router.put(
    "/{entity_id}",
    summary="Update an existing entity",
    response_model_exclude_none=True,
)
async def update_entity(
    entity_id: Annotated[Identifier, Path(...)],
    req: UpdateEntityRequest,
    service: Annotated[EntityService, Depends(get_entity_service)],
) -> EntityResponse:
    """Update an existing entity with the provided competency data and text to encode.

    This endpoint allows you to update an existing entity in the system.
    The `entity_id` should be provided in the path, and the `competency` should contain
    the updated data for the entity. It returns the updated entity as a response.

    Args:
        entity_id (Identifier): The unique identifier of the entity.
        req (UpdateEntityRequest): The request object with the updated entity data.
        service (EntityService): The entity service dependency.

    Returns:
        EntityResponse: The response object containing the updated entity.
    """
    entity = service.update_entity(
        identifier=entity_id,
        competency=req.competency,
        text=req.competency.indexed_text if req.competency.indexed_text else None,
    )
    return ApiEntityMapper.domain_to_adapter(entity)


@router.delete(
    "/{entity_id}",
    summary="Delete an entity",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_entity(
    entity_id: Annotated[Identifier, Path(...)],
    service: Annotated[EntityService, Depends(get_entity_service)],
) -> None:
    """Delete an entity by its ID.

    This endpoint allows you to delete an entity using its unique identifier.
    The `entity_id` should be provided in the path, and it will remove the entity
    from the system without returning any content.

    Args:
        entity_id (Identifier): The unique identifier of the entity.
        service (EntityService): The entity service dependency.

    Returns:
        None
    """
    service.delete_entity(identifier=entity_id)
