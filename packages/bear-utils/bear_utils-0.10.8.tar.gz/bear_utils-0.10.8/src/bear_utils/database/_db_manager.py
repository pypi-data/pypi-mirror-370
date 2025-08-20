"""Database Manager Module for managing database connections and operations."""

import atexit
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, ClassVar

from pydantic import SecretStr
from singleton_base import SingletonBase
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

from bear_utils.constants._lazy_typing import TableType


class DatabaseManager:
    _base: ClassVar[DeclarativeMeta | None] = None

    @classmethod
    def set_base(cls, base: DeclarativeMeta) -> None:
        """Set the base class for the database manager."""
        cls._base = base

    @classmethod
    def get_base(cls) -> DeclarativeMeta:
        """Get the base class for the database manager."""
        if cls._base is None:
            cls.set_base(declarative_base())
        if cls._base is None:
            raise ValueError("Base class is not set, failed to set base.")
        return cls._base

    def __init__(self, db_url: str | Path | None = None, default_schema: str = "sqlite:///"):
        if db_url is None or db_url == "":
            raise ValueError("Database URL cannot be None or empty.")
        if isinstance(db_url, str) and not db_url.startswith(default_schema):
            db_url = f"{default_schema}{db_url}"
        self.db_url: str = str(db_url)
        self.engine: Engine = create_engine(self.db_url, echo=False)
        base: DeclarativeMeta = DatabaseManager.get_base()
        self.metadata: MetaData = base.metadata
        self.SessionFactory: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.session: scoped_session[Session] = scoped_session(self.SessionFactory)
        atexit.register(self.close_all)
        self.create_tables()

    def get_all_records(self, table_obj: type[TableType]) -> list[TableType]:
        """Get all records from a table."""
        return self.session().query(table_obj).all()

    def count_records(self, table_obj: type[TableType]) -> int:
        """Count the number of records in a table."""
        return self.session().query(table_obj).count()

    def get_records_by_var(self, table_obj: type[TableType], variable: str, value: str) -> list[TableType]:
        """Get records from a table by a specific variable."""
        return self.session().query(table_obj).filter(getattr(table_obj, variable) == value).all()

    def count_records_by_var(self, table_obj: type[TableType], variable: str, value: str) -> int:
        """Count the number of records in a table by a specific variable."""
        return self.session().query(table_obj).filter(getattr(table_obj, variable) == value).count()

    @contextmanager
    def open_session(self) -> Generator[Session, Any]:
        """Provide a transactional scope around a series of operations."""
        session: Session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def get_session(self) -> Session:
        """Get a new session."""
        return self.session()

    def close_session(self) -> None:
        """Close the session."""
        self.session.remove()

    def create_tables(self) -> None:
        """Create all tables defined by Base"""
        self.metadata.create_all(self.engine)

    def close_all(self) -> None:
        """Close all sessions and connections."""
        self.session.close()
        self.engine.dispose()


class PostgresDB(DatabaseManager):
    """Postgres Database Manager, inherits from DatabaseManager for Postgres-specific operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "",
        password: str | SecretStr = "",
        db_name: str = "postgres",
    ) -> None:
        self.engine: Engine = create_engine(
            url=f"postgresql://{user}:{password.get_secret_value() if isinstance(password, SecretStr) else password}@{host}:{port}/{db_name}",
            echo=False,
        )
        base: DeclarativeMeta = DatabaseManager.get_base()
        self.metadata: MetaData = base.metadata
        self.SessionFactory: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.session: scoped_session[Session] = scoped_session(self.SessionFactory)
        atexit.register(self.close_all)
        self.create_tables()


class SingletonDB(DatabaseManager, SingletonBase):
    """Singleton class for DatabaseManager, uses SingletonBase to inject singleton pattern."""


__all__ = ["DatabaseManager", "SingletonDB"]
