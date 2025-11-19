from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, engine, SessionLocal, Base, Movie, Link, Rating, Tag
import csv
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        if db.query(Movie).count() == 0:
            print("Loading movies...")
            with open(os.path.join(data_dir, 'movies.csv'), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.add(Movie(movieId=int(row['movieId']), title=row['title'], genres=row['genres']))
            db.commit()

        if db.query(Link).count() == 0:
            print("Loading links...")
            with open(os.path.join(data_dir, 'links.csv'), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.add(Link(movieId=int(row['movieId']), imdbId=row['imdbId'], tmdbId=row['tmdbId']))
            db.commit()

        if db.query(Rating).count() == 0:
            print("Loading ratings...")
            with open(os.path.join(data_dir, 'ratings.csv'), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.add(Rating(userId=int(row['userId']), movieId=int(row['movieId']), rating=float(row['rating']), timestamp=int(row['timestamp'])))
            db.commit()

        if db.query(Tag).count() == 0:
            print("Loading tags...")
            with open(os.path.join(data_dir, 'tags.csv'), encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.add(Tag(userId=int(row['userId']), movieId=int(row['movieId']), tag=row['tag'], timestamp=int(row['timestamp'])))
            db.commit()
            
        print("Database initialized.")
    finally:
        db.close()
        
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()

@app.get("/links")
def get_links(db: Session = Depends(get_db)):
    return db.query(Link).all()

@app.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    return db.query(Rating).limit(100).all()

@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()
