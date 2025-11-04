"""Test module for domain exceptions."""

from domain.exceptions import (
    DomainError,
    EmbeddingError,
    EntityNotFoundError,
    ValidationError,
)


class TestDomainError:
    """Test class for DomainError."""

    def test_domain_error_is_exception(self) -> None:
        """Test that DomainError is an Exception."""
        error = DomainError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_domain_error_inheritance(self) -> None:
        """Test that all domain errors inherit from DomainError."""
        errors = [
            EntityNotFoundError,
            EmbeddingError,
            ValidationError,
        ]

        for error_class in errors:
            error = error_class("Test error")
            assert isinstance(error, DomainError)
            assert isinstance(error, Exception)


class TestEntityNotFoundError:
    """Test class for EntityNotFoundError."""

    def test_entity_not_found_error_message(self) -> None:
        """Test EntityNotFoundError with custom message."""
        error = EntityNotFoundError("Entity with ID 123 not found")
        assert str(error) == "Entity with ID 123 not found"

    def test_entity_not_found_error_inheritance(self) -> None:
        """Test EntityNotFoundError inheritance."""
        error = EntityNotFoundError("Test error")
        assert isinstance(error, DomainError)
        assert isinstance(error, Exception)


class TestEmbeddingError:
    """Test class for EmbeddingError."""

    def test_embedding_error_message(self) -> None:
        """Test EmbeddingError with custom message."""
        error = EmbeddingError("Failed to generate embedding")
        assert str(error) == "Failed to generate embedding"

    def test_embedding_error_inheritance(self) -> None:
        """Test EmbeddingError inheritance."""
        error = EmbeddingError("Test error")
        assert isinstance(error, DomainError)
        assert isinstance(error, Exception)


class TestValidationError:
    """Test class for ValidationError."""

    def test_validation_error_message(self) -> None:
        """Test ValidationError with custom message."""
        error = ValidationError("Invalid input data")
        assert str(error) == "Invalid input data"

    def test_validation_error_inheritance(self) -> None:
        """Test ValidationError inheritance."""
        error = ValidationError("Test error")
        assert isinstance(error, DomainError)
        assert isinstance(error, Exception)
