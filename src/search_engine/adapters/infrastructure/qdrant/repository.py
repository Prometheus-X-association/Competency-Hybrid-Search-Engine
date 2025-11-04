from collections.abc import Sequence
from typing import override
from uuid import uuid4

from logger import LoggerContract
from pydantic import ValidationError as PydanticValidationError
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchAny,
    MatchValue,
    NamedSparseVector,
    NamedVector,
    PointStruct,
    Prefetch,
    Range,
)
from qdrant_client.http.models import (
    SparseVector as QdrantSparseVector,
)

from adapters.exceptions import RepositoryError
from domain.contracts.repository import RepositoryContract
from domain.exceptions import ValidationError
from domain.types.competency import Competency
from domain.types.entity import Entity
from domain.types.filters import DomainFilter, DomainFilterOperator
from domain.types.identifier import Identifier
from domain.types.service_models import (
    CreateEntityModel,
    SearchResult,
    UpdateEntityModel,
)
from domain.types.vectors import DenseVector, SparseVector, VectorName


class QdrantRepository(RepositoryContract):
    """Implementation of RepositoryContract for Qdrant."""

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        logger: LoggerContract,
        dense_vector_name: str,
        sparse_vector_name: str,
    ) -> None:
        """Initialize the QdrantRepository.

        Args:
            client (QdrantClient): The Qdrant client instance.
            collection_name (str): Name of the Qdrant collection to use.
            logger (LoggerContract): Logger instance for logging.
            dense_vector_name (str): Name of the dense vector in Qdrant.
            sparse_vector_name (str): Name of the sparse vector in Qdrant.
        """
        self.client = client
        self.collection_name = collection_name
        self.logger = logger
        self.dense_vector_name = dense_vector_name
        self.sparse_vector_name = sparse_vector_name

    @override
    def create_entity(self, model: CreateEntityModel) -> Entity:
        """Creates a new entity in Qdrant.

        Args:
            model (CreateEntityModel): CreateEntityModel with `competency` and `vector`.

        Returns:
            Entity: The created entity with a generated identifier.
        """
        new_id = uuid4()

        # Convert Competency model to dict for storage in Qdrant
        competency_payload = model.competency.model_dump(exclude_none=True)

        # Store both dense and sparse vectors in Qdrant
        vectors = {
            self.dense_vector_name: model.dense_vector.values,
            self.sparse_vector_name: {
                "indices": model.sparse_vector.indices,
                "values": model.sparse_vector.values,
            },
        }

        point = PointStruct(
            id=str(new_id),
            vector=vectors,
            payload=competency_payload,
        )

        logger_context = {
            "id": new_id,
            "competency": competency_payload,
            "dense_vector_length": len(model.dense_vector.values),
            "sparse_vector_dimensions": len(model.sparse_vector.indices),
        }

        # Store the entity in Qdrant
        try:
            response = self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
        except Exception as e:
            self.logger.exception(
                "Failed to create entity",
                context=logger_context,
                exc=e,
            )
            raise RepositoryError(f"Failed to create entity: {e}") from e

        if str(response.status).lower() != "completed":
            self.logger.error(
                "Failed to create entity",
                context={"status": response.status, **logger_context},
            )
            raise RepositoryError(
                f"Failed to create entity: invalid response status {response.status}",
            )

        self.logger.info("Entity created", context={"id": new_id})
        return Entity(identifier=new_id, competency=model.competency)

    @override
    def get_entity(self, identifier: Identifier) -> Entity | None:
        """Retrieves an entity by its identifier.

        Args:
            identifier (Identifier): The UUID of the entity.

        Returns:
            Entity | None: The found entity or None if not found.
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[str(identifier)],
                with_payload=True,
                with_vectors=True,
            )
        except Exception as e:
            self.logger.exception(
                "Failed to retrieve entity",
                context={"id": identifier},
                exc=e,
            )
            raise RepositoryError(f"Failed to get entity ({identifier}): {e}") from e

        # If the entity does not exist
        if not points:
            self.logger.info(
                "Entity not found",
                context={"id": identifier},
            )
            return None

        point = points[0]

        # Convert payload dict back to Competency model
        competency = Competency(**point.payload)

        # Named vectors (new format)
        # Reconstruct DenseVector from stored values
        dense_data = point.vector.get(self.dense_vector_name, [])
        dense_vector = DenseVector(values=dense_data) if dense_data else None

        # Reconstruct SparseVector from stored indices and values
        sparse_data = point.vector.get(self.sparse_vector_name, {})
        if isinstance(sparse_data, dict):
            sparse_vector = SparseVector(
                indices=sparse_data.get("indices", []),
                values=sparse_data.get("values", []),
            )
        elif isinstance(sparse_data, QdrantSparseVector):
            sparse_vector = SparseVector(
                indices=sparse_data.indices if hasattr(sparse_data, "indices") else [],
                values=sparse_data.values if hasattr(sparse_data, "values") else [],
            )

        return Entity(
            identifier=identifier,
            competency=competency,
            dense_vector=dense_vector,
            sparse_vector=sparse_vector,
        )

    @override
    def update_entity(self, model: UpdateEntityModel) -> Entity:
        """Updates an existing entity (competency + vector).

        Args:
            model (UpdateEntityModel): UpdateEntityModel with `id`,
                `competency`, and `vector`.

        Returns:
            Entity: The updated entity.
        """
        # Convert Competency model to dict for storage in Qdrant
        competency_payload = model.competency.model_dump(exclude_none=True)

        # Store both dense and sparse vectors in Qdrant
        vectors = {
            self.dense_vector_name: model.dense_vector.values,
            self.sparse_vector_name: {
                "indices": model.sparse_vector.indices,
                "values": model.sparse_vector.values,
            },
        }

        point = PointStruct(
            id=str(model.identifier),
            vector=vectors,
            payload=competency_payload,
        )
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
        except Exception as e:
            self.logger.exception(
                "Failed to update entity",
                context={"id": model.identifier, "competency": competency_payload},
                exc=e,
            )
            raise RepositoryError(
                f"Failed to update entity ({model.identifier}): {e}",
            ) from e

        self.logger.info(
            "Entity updated successfully",
            context={"id": model.identifier},
        )

        return Entity(identifier=model.identifier, competency=model.competency)

    @override
    def delete_entity(self, identifier: Identifier) -> None:
        """Deletes an entity from Qdrant by its identifier.

        Args:
            identifier (Identifier): The UUID of the entity to delete.
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[str(identifier)],
            )
        except Exception as e:
            self.logger.exception(
                "Failed to delete entity",
                context={"id": identifier},
                exc=e,
            )
            raise RepositoryError(f"Failed to delete entity ({identifier}): {e}") from e

        self.logger.info(
            "Entity deleted successfully",
            context={"id": identifier},
        )

    @override
    def search_by_vector_and_filters(
        self,
        vector: DenseVector | SparseVector,
        filters: Sequence[DomainFilter],
        top: int,
        vector_name: VectorName = VectorName.DENSE,
    ) -> Sequence[SearchResult]:
        """Searches for similar entities to a given vector with filter criteria.

        Args:
            vector (DenseVector | SparseVector): The vector to search for.
            filters (Sequence[DomainFilter]): The filters criteria to apply.
            top (int): The number of results to return.
            vector_name (VectorName): The name of the vector to search with.

        Returns:
            Sequence[SearchResult]: A sequence of SearchResult objects.
        """
        self.logger.info(
            "Searching with filters",
            context={"filters": filters, "vector_name": vector_name},
        )

        try:
            qdrant_filter = self._build_search_filters(filters)
        except PydanticValidationError as e:
            self.logger.exception(
                "Validation error while building search filters",
                context={"filters": filters},
                exc=e,
            )
            raise ValidationError(f"Invalid filters: {e}") from e
        except Exception as e:
            self.logger.exception(
                "Failed to build search filters",
                context={"filters": filters},
                exc=e,
            )
            raise RepositoryError(f"Failed to build search filters: {e}") from e

        # Prepare query vector based on vector type
        if vector_name == VectorName.SPARSE:
            query_vector = NamedSparseVector(
                name=self.sparse_vector_name,
                vector={
                    "indices": vector.indices,
                    "values": vector.values,
                },
            )
        elif vector_name == VectorName.DENSE:
            query_vector = NamedVector(
                name=self.dense_vector_name,
                vector=vector.values,
            )
        else:
            raise RepositoryError(f"Unsupported vector type: {vector_name}")

        try:
            response = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=qdrant_filter,
                limit=top,
                with_payload=True,
            )
        except Exception as e:
            # Prepare vector info for logging
            vector_info = (
                {"dense_vector_length": len(vector.values)}
                if isinstance(vector, DenseVector)
                else {"sparse_dimensions": len(vector.indices)}
            )

            self.logger.exception(
                "Failed to search by vector and filters",
                context={
                    **vector_info,
                    "vector_name": vector_name,
                    "filters": filters,
                    "top": top,
                },
                exc=e,
            )
            raise RepositoryError(f"Failed search_by_vector : {e}") from e

        return [
            SearchResult(
                entity=Entity(
                    identifier=Identifier(point.id),
                    competency=Competency(**point.payload),
                ),
                score=point.score,
            )
            for point in response
        ]

    @override
    def search_hybrid_by_vectors_and_filters(
        self,
        dense_vector: DenseVector,
        sparse_vector: SparseVector,
        filters: Sequence[DomainFilter],
        top: int,
    ) -> Sequence[SearchResult]:
        """Searches using hybrid approach combining dense and sparse vectors.

        Args:
            dense_vector (DenseVector): The dense vector for semantic search.
            sparse_vector (SparseVector): The sparse vector for keyword search.
            filters (Sequence[DomainFilter]): The filters criteria to apply.
            top (int): The number of results to return.

        Returns:
            Sequence[SearchResult]: A sequence of SearchResult objects with
                hybrid scoring.
        """
        self.logger.info(
            "Performing hybrid search",
            context={
                "filters": filters,
                "top": top,
            },
        )

        try:
            qdrant_filter = self._build_search_filters(filters)
        except PydanticValidationError as e:
            self.logger.exception(
                "Validation error while building search filters",
                context={"filters": filters},
                exc=e,
            )
            raise ValidationError(f"Invalid filters: {e}") from e
        except Exception as e:
            self.logger.exception(
                "Failed to build search filters",
                context={"filters": filters},
                exc=e,
            )
            raise RepositoryError(f"Failed to build search filters: {e}") from e

        # Create dense and sparse vector queries
        dense_query = Prefetch(
            using=self.dense_vector_name,
            query=dense_vector.values,
            filter=qdrant_filter,
            limit=top,
        )

        sparse_query = Prefetch(
            using=self.sparse_vector_name,
            query={
                "indices": sparse_vector.indices,
                "values": sparse_vector.values,
            },
            filter=qdrant_filter,
            limit=top,
        )

        try:
            # Perform hybrid search using query_points
            response = self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[dense_query, sparse_query],
                query=FusionQuery(fusion=Fusion.RRF),
                query_filter=qdrant_filter,
                limit=top,
                with_payload=True,
            )
        except Exception as e:
            self.logger.exception(
                "Failed to perform hybrid search",
                context={
                    "dense_vector_length": len(dense_vector.values),
                    "sparse_dimensions": len(sparse_vector.indices),
                    "filters": filters,
                    "top": top,
                },
                exc=e,
            )
            raise RepositoryError(f"Failed hybrid search: {e}") from e

        return [
            SearchResult(
                entity=Entity(
                    identifier=Identifier(point.id),
                    competency=Competency(**point.payload),
                ),
                score=point.score,
            )
            for point in response.points
        ]

    @classmethod
    def _build_search_filters(cls, filters: Sequence[DomainFilter]) -> Filter:
        """Builds a Qdrant Filter from a sequence of DomainFilter objects.

        Args:
            filters (Sequence[DomainFilter]): A sequence of
                DomainFilter objects to convert.

        Returns:
            Filter: A Qdrant Filter object constructed from the provided filters.
        """
        if not filters:
            return Filter()

        must_conditions = []
        must_not_conditions = []

        for f in filters:
            condition = cls._create_field_condition(f)
            if f.operator in (
                DomainFilterOperator.NOT_EQUAL,
                DomainFilterOperator.NOT_IN,
            ):
                must_not_conditions.append(condition)
            else:
                must_conditions.append(condition)

        return Filter(
            must=must_conditions if must_conditions else None,
            must_not=must_not_conditions if must_not_conditions else None,
        )

    @staticmethod
    def _create_field_condition(domain_filter: DomainFilter) -> FieldCondition:
        """Creates a FieldCondition from a DomainFilter.

        Args:
            domain_filter (DomainFilter): The domain filter to convert.

        Returns:
            FieldCondition: The corresponding Qdrant FieldCondition.
        """
        match domain_filter.operator:
            case DomainFilterOperator.EQUAL | DomainFilterOperator.NOT_EQUAL:
                return FieldCondition(
                    key=domain_filter.field,
                    match=MatchValue(value=domain_filter.value),
                )
            case DomainFilterOperator.IN | DomainFilterOperator.NOT_IN:
                return FieldCondition(
                    key=domain_filter.field,
                    match=MatchAny(any=domain_filter.value),
                )
            case DomainFilterOperator.GREATER_THAN:
                return FieldCondition(
                    key=domain_filter.field,
                    range=Range(gt=domain_filter.value),
                )
            case DomainFilterOperator.GREATER_THAN_OR_EQUAL:
                return FieldCondition(
                    key=domain_filter.field,
                    range=Range(gte=domain_filter.value),
                )
            case DomainFilterOperator.LESS_THAN:
                return FieldCondition(
                    key=domain_filter.field,
                    range=Range(lt=domain_filter.value),
                )
            case DomainFilterOperator.LESS_THAN_OR_EQUAL:
                return FieldCondition(
                    key=domain_filter.field,
                    range=Range(lte=domain_filter.value),
                )
