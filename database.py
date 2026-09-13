from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


# SQLite database
DATABASE_URL = "sqlite:///./repomind.db"


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Create base class
Base = declarative_base()


# Create Analysis table
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    repository_name = Column(String)
    owner = Column(String)

    stars = Column(Integer)
    forks = Column(Integer)
    open_issues = Column(Integer)

    analyzed_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)


# Create database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)