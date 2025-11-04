"""Test module for UUID type."""

from uuid import UUID, uuid4

from domain.types.identifier import Identifier


class TestIdentifier:
    """Test class for Identifier type alias."""

    def test_identifier_is_uuid(self) -> None:
        """Test that Identifier is an alias for UUID."""
        # Identifier should be the same as UUID
        assert Identifier is UUID

    def test_identifier_creation(self) -> None:
        """Test creating an Identifier."""
        # Using uuid4() to create a random UUID
        identifier = uuid4()

        # Should be an instance of both UUID and Identifier
        assert isinstance(identifier, UUID)
        assert isinstance(identifier, Identifier)

    def test_identifier_from_string(self) -> None:
        """Test creating Identifier from string."""
        uuid_string = "550e8400-e29b-41d4-a716-446655440000"
        identifier = Identifier(uuid_string)

        assert isinstance(identifier, UUID)
        assert isinstance(identifier, Identifier)
        assert str(identifier) == uuid_string

    def test_identifier_equality(self) -> None:
        """Test Identifier equality."""
        uuid_string = "550e8400-e29b-41d4-a716-446655440000"

        identifier1 = Identifier(uuid_string)
        identifier2 = Identifier(uuid_string)
        identifier3 = uuid4()

        assert identifier1 == identifier2
        assert identifier1 != identifier3
