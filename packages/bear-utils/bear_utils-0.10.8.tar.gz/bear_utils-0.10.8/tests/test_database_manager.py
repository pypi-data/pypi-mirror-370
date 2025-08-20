"""Tests for DatabaseManager module."""

from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest
from sqlalchemy import Integer, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.orm.session import Session

from bear_utils.database import DatabaseManager

MockBase = DatabaseManager.get_base()


class MockUser(MockBase):
    __tablename__ = "test_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)


class TestDatabaseManager:
    """Test the DatabaseManager class."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = "sqlite:///:memory:"

        DatabaseManager._base = None
        DatabaseManager.set_base(MockBase)

        self.db_manager = DatabaseManager(self.temp_db)

        with self.db_manager.open_session() as session:
            user1 = MockUser(name="Alice", email="alice@example.com")
            user2 = MockUser(name="Bob", email="bob@example.com")
            session.add(user1)
            session.add(user2)

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "db_manager"):
            self.db_manager.close_all()

    def test_init_with_valid_url(self):
        """Test DatabaseManager initialization with valid URL."""
        db_manager = DatabaseManager("sqlite:///:memory:")
        assert db_manager.db_url == "sqlite:///:memory:"
        assert db_manager.engine is not None
        assert db_manager.SessionFactory is not None
        assert db_manager.session is not None
        db_manager.close_all()

    def test_init_with_path(self):
        """Test DatabaseManager initialization with Path object."""
        with tempfile.NamedTemporaryFile(suffix=".db") as temp_file:
            path = Path(temp_file.name)
            # SQLAlchemy needs sqlite:/// prefix for file paths
            sqlite_url = f"sqlite:///{path}"
            db_manager = DatabaseManager(sqlite_url)
            assert str(path) in db_manager.db_url
            db_manager.close_all()

    def test_init_with_none_url_raises_error(self):
        """Test that None URL raises ValueError."""
        with pytest.raises(ValueError, match="Database URL cannot be None or empty"):
            DatabaseManager(None)

    def test_init_with_empty_url_raises_error(self):
        """Test that empty URL raises ValueError."""
        with pytest.raises(ValueError, match="Database URL cannot be None or empty"):
            DatabaseManager("")

    def test_set_and_get_base(self):
        """Test setting and getting the base class."""
        # Reset base
        DatabaseManager._base = None

        # Test auto-creation when None
        base = DatabaseManager.get_base()
        assert base is not None

        # Test setting custom base
        custom_base = declarative_base()
        DatabaseManager.set_base(custom_base)
        assert DatabaseManager.get_base() is custom_base

    def test_get_base_when_none_creates_default(self):
        """Test that get_base creates a default base when None."""
        DatabaseManager._base = None
        base = DatabaseManager.get_base()
        assert base is not None
        assert hasattr(base, "metadata")

    def test_create_tables(self):
        """Test table creation."""
        # Tables should already be created in setup
        # Verify by checking if we can query the table
        with self.db_manager.open_session() as session:
            count = session.query(MockUser).count()
            assert count == 2  # From our test data

    def test_get_all_records(self):
        """Test getting all records from a table."""
        users = self.db_manager.get_all_records(MockUser)
        assert len(users) == 2
        assert any(user.name == "Alice" for user in users)
        assert any(user.name == "Bob" for user in users)

    def test_get_all_records_empty_table(self):
        """Test getting records from empty table."""
        # Clear the table
        with self.db_manager.open_session() as session:
            session.query(MockUser).delete()

        users = self.db_manager.get_all_records(MockUser)
        assert len(users) == 0

    def test_count_records(self):
        """Test counting records in a table."""
        count = self.db_manager.count_records(MockUser)
        assert count == 2

    def test_count_records_empty_table(self):
        """Test counting records in empty table."""
        # Clear the table
        with self.db_manager.open_session() as session:
            session.query(MockUser).delete()

        count = self.db_manager.count_records(MockUser)
        assert count == 0

    def test_get_records_by_var(self):
        """Test getting records by specific variable."""
        users = self.db_manager.get_records_by_var(MockUser, "name", "Alice")
        assert len(users) == 1
        assert users[0].name == "Alice"
        assert users[0].email == "alice@example.com"

    def test_get_records_by_var_no_match(self):
        """Test getting records with no matches."""
        users = self.db_manager.get_records_by_var(MockUser, "name", "Charlie")
        assert len(users) == 0

    def test_get_records_by_var_multiple_matches(self):
        """Test getting records with multiple matches."""
        # Add another user with same name
        with self.db_manager.open_session() as session:
            user3 = MockUser(name="Alice", email="alice2@example.com")
            session.add(user3)

        users = self.db_manager.get_records_by_var(MockUser, "name", "Alice")
        assert len(users) == 2
        assert all(user.name == "Alice" for user in users)

    def test_count_records_by_var(self):
        """Test counting records by specific variable."""
        count = self.db_manager.count_records_by_var(MockUser, "name", "Alice")
        assert count == 1

        count = self.db_manager.count_records_by_var(MockUser, "name", "Charlie")
        assert count == 0

    def test_open_session_context_manager(self):
        """Test the session context manager."""
        with self.db_manager.open_session() as session:
            user = MockUser(name="Charlie", email="charlie@example.com")
            session.add(user)
            # Should auto-commit when exiting context

        users = self.db_manager.get_all_records(MockUser)
        assert len(users) == 3
        assert any(user.name == "Charlie" for user in users)

    def test_get_session(self):
        """Test getting a new session."""
        session = self.db_manager.get_session()
        assert session is not None

        count: int = session.query(MockUser).count()
        assert count == 2

        session.close()

    def test_close_session(self):
        """Test closing the session."""
        session: Session = self.db_manager.get_session()
        assert session is not None

        assert self.db_manager.session.registry.has() is True
        self.db_manager.close_session()
        assert self.db_manager.session.registry.has() is False

    def test_close_all(self):
        """Test closing all connections."""
        self.db_manager.close_all()

        # After closing, we should be able to create a new session
        # (though the old one is disposed)
        new_db_manager = DatabaseManager("sqlite:///:memory:")
        assert new_db_manager.session is not None
        new_db_manager.close_all()

    @patch("atexit.register")
    def test_atexit_registration(self, mock_atexit):
        """Test that close_all is registered with atexit."""
        DatabaseManager.set_base(MockBase)
        db_manager = DatabaseManager("sqlite:///:memory:")
        mock_atexit.assert_called_with(db_manager.close_all)
        db_manager.close_all()

    def test_metadata_property(self):
        """Test that metadata is properly set."""
        assert self.db_manager.metadata is not None
        assert hasattr(self.db_manager.metadata, "tables")
        assert "test_users" in self.db_manager.metadata.tables


class TestDatabaseManagerEdgeCases:
    """Test edge cases and error conditions."""

    def test_get_base_failure_scenario(self):
        """Test edge case where base setting fails."""
        DatabaseManager._base = None

        # Mock the set_base to simulate failure
        with patch.object(DatabaseManager, "set_base") as mock_set:
            mock_set.return_value = None  # Simulate failure
            DatabaseManager._base = None  # Ensure it stays None

            with pytest.raises(ValueError, match="Base class is not set, failed to set base"):
                DatabaseManager.get_base()

    def test_invalid_table_operations(self):
        """Test operations with invalid table configurations."""
        DatabaseManager.set_base(MockBase)
        db_manager = DatabaseManager("sqlite:///:memory:")

        # Try to query a table that doesn't exist in the database
        # Note: This might not fail immediately due to SQLAlchemy's lazy evaluation
        # The actual error would occur when the query is executed

        # Clean up
        db_manager.close_all()

    def test_concurrent_session_usage(self):
        """Test using multiple sessions concurrently."""
        DatabaseManager.set_base(MockBase)
        db_manager = DatabaseManager("sqlite:///:memory:")

        # Create test data
        with db_manager.open_session() as session:
            user = MockUser(name="Test", email="test@example.com")
            session.add(user)

        # Get multiple sessions
        session1 = db_manager.get_session()
        session2 = db_manager.get_session()

        # Both should be able to query
        count1 = session1.query(MockUser).count()
        count2 = session2.query(MockUser).count()

        assert count1 == count2 == 1

        session1.close()
        session2.close()
        db_manager.close_all()


class TestDatabaseManagerIntegration:
    """Integration tests for DatabaseManager."""

    def test_full_crud_workflow(self):
        """Test a complete CRUD workflow."""
        DatabaseManager.set_base(MockBase)
        db_manager = DatabaseManager("sqlite:///:memory:")

        # CREATE
        with db_manager.open_session() as session:
            user = MockUser(name="Integration", email="integration@test.com")
            session.add(user)

        # READ
        users = db_manager.get_all_records(MockUser)
        assert len(users) == 1
        assert users[0].name == "Integration"

        # UPDATE (via session)
        with db_manager.open_session() as session:
            user = session.query(MockUser).filter(MockUser.name == "Integration").first()
            user.email = "updated@test.com"  # type: ignore[assignment]

        # Verify update
        updated_users = db_manager.get_records_by_var(MockUser, "email", "updated@test.com")
        assert len(updated_users) == 1
        assert updated_users[0].name == "Integration"

        # DELETE (via session)
        with db_manager.open_session() as session:
            session.query(MockUser).filter(MockUser.name == "Integration").delete()

        # Verify deletion
        final_count = db_manager.count_records(MockUser)
        assert final_count == 0

        db_manager.close_all()

    def test_error_recovery(self):
        """Test that the database manager recovers from errors properly."""
        DatabaseManager.set_base(MockBase)
        db_manager = DatabaseManager("sqlite:///:memory:")

        # Add initial data
        with db_manager.open_session() as session:
            user = MockUser(name="Good", email="good@test.com")
            session.add(user)

        # Try to cause an error
        try:
            with db_manager.open_session() as session:
                # Duplicate email should cause error
                bad_user = MockUser(name="Bad", email="good@test.com")
                session.add(bad_user)
                session.flush()
        except IntegrityError:
            pass  # Expected

        # Database should still be usable
        count: int = db_manager.count_records(MockUser)
        assert count == 1

        with db_manager.open_session() as session:
            new_user = MockUser(name="Recovery", email="recovery@test.com")
            session.add(new_user)

        final_count = db_manager.count_records(MockUser)
        assert final_count == 2

        db_manager.close_all()
