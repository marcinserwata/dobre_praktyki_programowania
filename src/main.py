from fastapi import FastAPI
from data_loader import load_data, Movie, Link, Rating, Tag

app = FastAPI()

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies")
def get_movies():
    return load_data("movies.csv", Movie)

@app.get("/links")
def get_links():
    return load_data("links.csv", Link)

@app.get("/ratings")
def get_ratings():
    return load_data("ratings.csv", Rating)

@app.get("/tags")
def get_tags():
    return load_data("tags.csv", Tag)
