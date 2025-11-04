from typing import Annotated

from fastapi import Form, HTTPException, status

from .enums import IndexingStrategy, Provider
from .indexing_strategies.contract import IndexingStrategyContract
from .indexing_strategies.field_combination import FieldCombinationStrategy
from .indexing_strategies.field_duplication import FieldDuplicationStrategy
from .mappers.contract import MapperContract
from .mappers.esco import EscoMapper
from .mappers.forma import FormaMapper
from .mappers.forma14 import Forma14Mapper
from .mappers.rome import RomeMapper
from .schemas import DataImportRequest

MAPPER_REGISTRY: dict[Provider, type[MapperContract]] = {
    Provider.ESCO: EscoMapper,
    Provider.ROME: RomeMapper,
    Provider.FORMA: FormaMapper,
    Provider.FORMA14: Forma14Mapper,
}

INDEXING_STRATEGY = {
    IndexingStrategy.FIELD_DUPLICATION: FieldDuplicationStrategy,
    IndexingStrategy.FIELD_COMBINATION: FieldCombinationStrategy,
}

DEFAULT_STRATEGY = [
    "title",
    "description",
    "category",
    "keywords",
]


async def get_mapper(provider: Provider) -> MapperContract | None:
    """Get the mapper for the given provider.

    This function retrieves the mapper class associated with the specified provider.
    If no mapper is registered for the provider,
    it raises an HTTPException with a 400 status code.

    Args:
        provider (Provider): The provider for which to get the mapper.

    Raises:
        HTTPException: If no mapper is registered for the provider.

    Returns:
        MapperContract: The mapper class for the specified provider.
    """
    mapper = MAPPER_REGISTRY.get(provider)
    if mapper is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"No mapper registered for provider='{provider.value}'."),
        )
    return mapper


async def mapper_dependency(
    request: DataImportRequest,
) -> MapperContract:
    """Dependency to get the mapper based on the request provider.

    Args:
        request (DataImportRequest): The request containing the provider information.

    Returns:
        MapperContract: The mapper class for the specified provider.
    """
    return await get_mapper(request.provider)


async def mapper_dependency_file(
    provider: Annotated[Provider, Form()],
) -> type[MapperContract]:
    """Dependency to get the mapper based on the provider from form data.

    Args:
        provider (Provider): The provider from form data.

    Returns:
        Type[MapperContract]: The mapper class for the specified provider.
    """
    return await get_mapper(provider)


async def get_indexing_strat(
    fields_to_index: list[str] | str | None,
    indexing_strategy: IndexingStrategy,
) -> IndexingStrategyContract:
    """Get the appropriate indexing strategy based on the fields and strategy type.

    Args:
        fields_to_index (list[str] | str | None): The fields to index.
        indexing_strategy (IndexingStrategy): The indexing strategy to use.

    Raises:
        HTTPException: If the indexing strategy is unsupported.

    Returns:
        IndexingStrategyContract: The appropriate indexing strategy.
    """
    if indexing_strategy not in INDEXING_STRATEGY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported indexing strategy: {indexing_strategy}",
        )

    strategy_class = INDEXING_STRATEGY[indexing_strategy]

    if isinstance(fields_to_index, str):
        fields_to_index = [
            field.strip() for field in fields_to_index.split(",") if field.strip()
        ]
    elif isinstance(fields_to_index, list):
        fields_to_index = [field.strip() for field in fields_to_index if field.strip()]
    else:
        fields_to_index = []

    if len(fields_to_index) > 0:
        return strategy_class(fields=fields_to_index)

    # If no fields are specified, use the default strategy
    return FieldDuplicationStrategy(fields=DEFAULT_STRATEGY)


async def get_indexing_strategy(
    request: DataImportRequest,
) -> IndexingStrategyContract:
    """Get the indexing strategy based on the request.

    Args:
        request (DataImportRequest): The request containing the indexing information.

    Returns:
        IndexingStrategyContract: The indexing strategy for the request.
    """
    return await get_indexing_strat(
        fields_to_index=request.fields_to_index,
        indexing_strategy=request.indexing_strategy,
    )


async def get_indexing_strategy_file(
    indexing_strategy: Annotated[
        IndexingStrategy,
        Form(),
    ] = IndexingStrategy.FIELD_DUPLICATION,
    fields_to_index: Annotated[str | None, Form()] = ",".join(DEFAULT_STRATEGY),
) -> IndexingStrategyContract:
    """Get the indexing strategy based on form data.

    Args:
        indexing_strategy (IndexingStrategy | None):
            The indexing strategy to use. Defaults to field duplication.
        fields_to_index (str | None): The fields to index.
            Defaults to a comma-separated string of default fields.

    Returns:
        IndexingStrategyContract: The indexing strategy for the form data.
    """
    return await get_indexing_strat(
        fields_to_index=fields_to_index,
        indexing_strategy=indexing_strategy,
    )
