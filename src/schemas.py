from pydantic import BaseModel, ConfigDict
from typing import Optional

class MovieBase(BaseModel):
    title: str
    genres: str

class MovieCreate(MovieBase):
    movieId: int

class Movie(MovieBase):
    movieId: int

    model_config = ConfigDict(from_attributes=True)

class LinkBase(BaseModel):
    imdbId: str
    tmdbId: str

class LinkCreate(LinkBase):
    movieId: int

class Link(LinkBase):
    movieId: int

    model_config = ConfigDict(from_attributes=True)

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

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    roles: list[str]

    model_config = ConfigDict(from_attributes=True)

class LoginData(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserDetails(BaseModel):
    username: str
    roles: list[str]
