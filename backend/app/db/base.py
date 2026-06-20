"""SQLAlchemy declarative base for all ORM models.

All model classes inherit from this Base, which SQLAlchemy uses
to track table metadata for migrations and queries.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models in the application."""

    pass