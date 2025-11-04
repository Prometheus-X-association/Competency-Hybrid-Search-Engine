from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from logger import LogLevel, LoguruLogger

from adapters.api.dependencies import get_db_client
from adapters.api.entity.router import router as entity_router
from adapters.api.exception_handler import ExceptionHandler
from adapters.api.search.router import router as search_router
from adapters.encoding.huggingface_dense import HuggingfaceEmbeddingService
from adapters.encoding.huggingface_sparse import HuggingfaceSparseEmbeddingService
from adapters.infrastructure.config.settings import Settings

config = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    """Lifespan context manager for FastAPI application.

    This function initializes the application with configuration and logger,
    yielding a dictionary containing the configuration and logger instances.
    It logs the startup and shutdown events of the application.

    Args:
        _app (FastAPI): The FastAPI application instance.

    Yields:
        Iterator[AsyncGenerator[dict[str, Any], None]]: A generator, that yields
            a dictionary containing the configuration and logger instances.
    """
    logger = LoguruLogger(level=config.get_log_level())
    logger.info(
        "Application startup",
        {
            "log_level": config.get_log_level().name,
            "environment": config.get_environment().name,
        },
    )

    logger.debug("Loading embedding model")
    model = HuggingfaceEmbeddingService.load_sentence_embeddings_model(
        model_name=config.get_embedding_model_name(),
    )

    # Load sparse embedding model
    logger.debug("Loading sparse embedding model")
    sparse_model = HuggingfaceSparseEmbeddingService.load_sparse_encoding_model(
        model_name=config.get_sparse_embedding_model_name(),
    )

    logger.debug("Creating DB collection if it does not exist yet")
    client = await get_db_client(logger=logger, config=config)
    client.create_db_collection_if_not_exists(
        collection_name=config.get_db_collection(),
        vector_dimensions=config.get_db_vector_dimensions(),
        vector_distance=config.get_db_vector_distance(),
        dense_vector_name=config.get_dense_vector_name(),
        sparse_vector_name=config.get_sparse_vector_name(),
    )

    logger.info("Application initialized successfully")

    yield {
        "config": config,
        "logger": logger,
        "model": model,
        "sparse_model": sparse_model,
    }
    logger.info("Application shutdown")


app = FastAPI(
    title="Search Engine API",
    version="0.0.1",
    debug=config.get_log_level() == LogLevel.DEBUG and not config.is_env_production(),
    lifespan=lifespan,
)
app.openapi_version = "3.0.2"

# Application exception handling configuration
exception_handler = ExceptionHandler()
exception_handler.configure(app=app)

# Include routers
app.include_router(entity_router)
app.include_router(search_router)
