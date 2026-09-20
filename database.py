from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    relationship
)

from datetime import datetime


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DATABASE_URL = "sqlite:///./repomind.db"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Create base class
Base = declarative_base()


# ==================================================
# REPOSITORY TABLE
# ==================================================

class Repository(Base):

    __tablename__ = "repositories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    owner = Column(
        String,
        nullable=False
    )

    name = Column(
        String,
        nullable=False
    )

    url = Column(
        String,
        unique=True,
        nullable=False
    )

    # One repository can have many analyses
    analyses = relationship(
        "Analysis",
        back_populates="repository"
    )


# ==================================================
# ANALYSIS TABLE
# ==================================================

class Analysis(Base):

    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    repository_id = Column(
        Integer,
        ForeignKey("repositories.id"),
        nullable=False
    )

    stars = Column(Integer)

    forks = Column(Integer)

    open_issues = Column(Integer)

    analyzed_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Connect analysis to repository
    repository = relationship(
        "Repository",
        back_populates="analyses"
    )


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

Base.metadata.create_all(
    bind=engine
)


# ==================================================
# DATABASE SESSION
# ==================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,

    # IMPORTANT:
    # Keep object values available after commit.
    expire_on_commit=False
)