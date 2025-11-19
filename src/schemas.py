from pydantic import BaseModel, ConfigDict
from typing import Optional

# Movie Schemas
class MovieBase(BaseModel):
    title: str
    genres: str

class MovieCreate(MovieBase):
    movieId: int

class Movie(MovieBase):
    movieId: int

    model_config = ConfigDict(from_attributes=True)

# Link Schemas
class LinkBase(BaseModel):
    imdbId: str
    tmdbId: str

class LinkCreate(LinkBase):
    movieId: int

class Link(LinkBase):
    movieId: int

    model_config = ConfigDict(from_attributes=True)

# Rating Schemas
class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# Tag Schemas
class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
