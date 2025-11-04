import json
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile, status

from adapters.api.entity.schemas import CreateEntityRequest

from .config import settings
from .dependencies import (
    get_indexing_strategy,
    get_indexing_strategy_file,
    mapper_dependency,
    mapper_dependency_file,
)
from .indexing_strategies.contract import IndexingStrategyContract
from .mappers.contract import MapperContract
from .schemas import CompetencyType, DataImportRequest, Language, Provider

app = FastAPI(
    title="Data Importer Service",
    version="1.0.0",
)
app.openapi_version = "3.0.2"


@app.post(
    "/import",
    status_code=status.HTTP_201_CREATED,
)
async def import_item(
    request: DataImportRequest,
    mapper: Annotated[type[MapperContract], Depends(mapper_dependency)],
    indexing_strategy: Annotated[
        IndexingStrategyContract,
        Depends(get_indexing_strategy),
    ],
) -> None:
    """Import a single item into the system.

    Args:
        request (DataImportRequest): The request containing the data to import.
        mapper (type[MapperContract]): The mapper to use for the import.
        indexing_strategy (IndexingStrategyContract): The indexing strategy to use.

    Raises:
        HTTPException: If the import fails.
    """
    # Create a mapper instance based on the request parameters
    mapper_instance: MapperContract = mapper(
        provider=request.provider,
        competency_type=request.competency_type,
        lang=request.lang,
        **request.data,
    )

    # Run the mapping process to convert the raw data into a Competency object
    mapped_competency = mapper_instance.to_competency()

    # Apply the indexing strategy to expand the competency
    expanded_competencies = indexing_strategy.expand_competency(mapped_competency)

    # Create requests for the search engine
    entity_requests = [
        CreateEntityRequest(
            competency=comp.model_dump(mode="json", exclude_none=True),
        )
        for comp in expanded_competencies
    ]

    # Forward to the main Search-Engine API
    async with httpx.AsyncClient() as client:
        try:
            # Because I can only send a CreateEntityRequest at a time,
            # I need to loop through the competencies
            # and send them one by one.
            for req in entity_requests:
                resp = await client.post(
                    settings.search_engine_endpoint,
                    json=req.model_dump(mode="json", exclude_none=True),
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                    timeout=60.0,
                )
                resp.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error connecting to main service: {exc}",
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=(
                    f"Main service error {exc.response.status_code}: "
                    f"{exc.response.text}"
                ),
            ) from exc


@app.post(
    "/import/file",
    description="Import a JSON file containing an item per row.",
    status_code=status.HTTP_201_CREATED,
)
async def import_file(
    file: UploadFile,
    provider: Annotated[Provider, Form(description="The provider of the competency.")],
    competency_type: Annotated[
        CompetencyType,
        Form(description="The type of competency to import."),
    ],
    mapper: Annotated[type[MapperContract], Depends(mapper_dependency_file)],
    indexing_strategy: Annotated[
        IndexingStrategyContract,
        Depends(get_indexing_strategy_file),
    ],
    lang: Annotated[
        Language,
        Form(description="The language of the competency. Default is French."),
    ] = Language.FR,
) -> None:
    """Import a JSON file containing an item per row.

    Args:
        file (UploadFile): The JSON file to import.
        provider (Provider | None): The provider of the competency.
        competency_type (CompetencyType | None): The type of competency to import.
        mapper (type[MapperContract]): The mapper to use for the import.
        indexing_strategy (IndexingStrategyContract): The indexing strategy to use.
        lang (Language | None): The language of the competency. Default to French.

    Raises:
        HTTPException: If the JSON file is invalid or not an array.
    """
    try:
        data = json.loads(await file.read())
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format: {exc}",
        ) from exc

    if not isinstance(data, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON must be an array of items.",
        )

    for item in data:
        request = DataImportRequest(
            data=item,
            provider=provider,
            competency_type=competency_type,
            lang=lang,
        )
        await import_item(request, mapper, indexing_strategy)
