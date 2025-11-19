from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'movies.db')}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"

    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genres = Column(String)

class Link(Base):
    __tablename__ = "links"

    movieId = Column(Integer, primary_key=True, index=True)
    imdbId = Column(String)
    tmdbId = Column(String)

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, index=True)
    movieId = Column(Integer, index=True)
    rating = Column(Float)
    timestamp = Column(Integer)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, index=True)
    movieId = Column(Integer, index=True)
    tag = Column(String)
    timestamp = Column(Integer)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
