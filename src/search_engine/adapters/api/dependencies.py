from typing import Annotated

from fastapi import Depends, Request
from logger import LoggerContract
from sentence_transformers import SentenceTransformer
from sentence_transformers.sparse_encoder import SparseEncoder

from adapters.encoding.huggingface_dense import HuggingfaceEmbeddingService
from adapters.encoding.huggingface_sparse import HuggingfaceSparseEmbeddingService
from adapters.infrastructure.config.contract import ConfigContract
from adapters.infrastructure.qdrant.client import QdrantClientWrapper
from adapters.infrastructure.qdrant.repository import QdrantRepository
from domain.contracts.db_client import ClientWrapperContract
from domain.contracts.embedding_service import EmbeddingServiceContract
from domain.contracts.repository import RepositoryContract
from domain.contracts.sparse_embedding_service import SparseEmbeddingServiceContract
from domain.services.entity_service import EntityService


async def get_config(request: Request) -> ConfigContract:
    """Returns the ConfigContract instance from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        ConfigContract: The configuration settings for the application.
    """
    return request.state.config


async def get_logger(request: Request) -> LoggerContract:
    """Returns the LoggerContract instance from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        LoggerContract: The logger instance for the application.
    """
    return request.state.logger


async def get_embedding_model(
    request: Request,
) -> SentenceTransformer:
    """Gets the embedding model from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        SentenceTransformer: The embedding model.
    """
    return request.state.model


async def get_sparse_embedding_model(
    request: Request,
) -> SparseEncoder:
    """Gets the sparse embedding model from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        SparseEncoder: The sparse embedding model.
    """
    return request.state.sparse_model


async def get_db_client(
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> ClientWrapperContract:
    """Creates and returns the implementation of ClientWrapperContract.

    This function initializes a QdrantClientWrapper with the provided configuration
    and logger.

    Args:
        config (ConfigContract): The configuration settings for the application.
        logger (LoggerContract): The logger instance for logging.

    Returns:
        ClientWrapperContract: The implementation of the ClientWrapperContract.
    """
    return QdrantClientWrapper(
        url=config.get_db_url(),
        api_key=config.get_db_api_key(),
        logger=logger,
    )


async def get_repository(
    client: Annotated[ClientWrapperContract, Depends(get_db_client)],
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> RepositoryContract:
    """Creates and returns the implementation of RepositoryContract.

    This function initializes a QdrantRepository with the provided configuration
    and logger. It is used to interact with the Qdrant vector database.

    Args:
        client (ClientWrapperContract): The Qdrant client wrapper instance.
        config (ConfigContract): The configuration settings for the application.
        logger (LoggerContract): The logger instance for logging.

    Returns:
        RepositoryContract: The implementation of the RepositoryContract.
    """
    return QdrantRepository(
        client=client.get_client(),
        collection_name=config.get_db_collection(),
        logger=logger,
        dense_vector_name=config.get_dense_vector_name(),
        sparse_vector_name=config.get_sparse_vector_name(),
    )


async def get_dense_embedding_service(
    model: Annotated[SentenceTransformer, Depends(get_embedding_model)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> EmbeddingServiceContract:
    """Creates and returns the dense embedding service.

    Args:
        model (SentenceTransformer): The Hugging Face model for dense embeddings.
        logger (LoggerContract): The logger instance for logging.

    Returns:
        EmbeddingServiceContract: The dense embedding service implementation.
    """
    return HuggingfaceEmbeddingService(logger=logger, model=model)


async def get_sparse_embedding_service(
    sparse_model: Annotated[SparseEncoder, Depends(get_sparse_embedding_model)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> SparseEmbeddingServiceContract:
    """Creates and returns the sparse embedding service.

    Args:
        sparse_model (SparseEncoder): The sparse embedding model.
        logger (LoggerContract): The logger instance for logging.

    Returns:
        SparseEmbeddingServiceContract: The sparse embedding service implementation.
    """
    return HuggingfaceSparseEmbeddingService(logger=logger, model=sparse_model)


async def get_entity_service(
    repository: Annotated[RepositoryContract, Depends(get_repository)],
    dense_embedding_service: Annotated[
        EmbeddingServiceContract,
        Depends(get_dense_embedding_service),
    ],
    sparse_embedding_service: Annotated[
        SparseEmbeddingServiceContract,
        Depends(get_sparse_embedding_service),
    ],
) -> EntityService:
    """Creates and returns the implementation of EntityService.

    This function initializes an EntityService with the provided repository
    and both embedding services. It is used to manage entities in the search engine.

    Args:
        repository (RepositoryContract): The repository dependency.
        dense_embedding_service (EmbeddingServiceContract):
            The dense embedding service dependency.
        sparse_embedding_service (SparseEmbeddingServiceContract):
            The sparse embedding service dependency.

    Returns:
        EntityService: The implementation of the EntityService.
    """
    return EntityService(
        repository=repository,
        dense_embedding_service=dense_embedding_service,
        sparse_embedding_service=sparse_embedding_service,
    )
