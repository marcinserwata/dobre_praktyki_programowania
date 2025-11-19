from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import database
import schemas
import csv
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    database.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        if db.query(database.Movie).count() == 0:
            print("Loading movies...")
            if os.path.exists(os.path.join(data_dir, 'movies.csv')):
                with open(os.path.join(data_dir, 'movies.csv'), encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        db.add(database.Movie(movieId=int(row['movieId']), title=row['title'], genres=row['genres']))
                db.commit()

        if db.query(database.Link).count() == 0:
            print("Loading links...")
            if os.path.exists(os.path.join(data_dir, 'links.csv')):
                with open(os.path.join(data_dir, 'links.csv'), encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        db.add(database.Link(movieId=int(row['movieId']), imdbId=row['imdbId'], tmdbId=row['tmdbId']))
                db.commit()

        if db.query(database.Rating).count() == 0:
            print("Loading ratings...")
            if os.path.exists(os.path.join(data_dir, 'ratings.csv')):
                with open(os.path.join(data_dir, 'ratings.csv'), encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        db.add(database.Rating(userId=int(row['userId']), movieId=int(row['movieId']), rating=float(row['rating']), timestamp=int(row['timestamp'])))
                db.commit()

        if db.query(database.Tag).count() == 0:
            print("Loading tags...")
            if os.path.exists(os.path.join(data_dir, 'tags.csv')):
                with open(os.path.join(data_dir, 'tags.csv'), encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        db.add(database.Tag(userId=int(row['userId']), movieId=int(row['movieId']), tag=row['tag'], timestamp=int(row['timestamp'])))
                db.commit()
            
        print("Database initialized.")
    finally:
        db.close()
        
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/movies", response_model=List[schemas.Movie])
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(database.Movie).offset(skip).limit(limit).all()

@app.post("/movies", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(database.get_db)):
    db_movie = db.query(database.Movie).filter(database.Movie.movieId == movie.movieId).first()
    if db_movie:
        raise HTTPException(status_code=400, detail="Movie already exists")
    new_movie = database.Movie(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def get_movie(movie_id: int, db: Session = Depends(database.get_db)):
    db_movie = db.query(database.Movie).filter(database.Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db_movie

@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie: schemas.MovieCreate, db: Session = Depends(database.get_db)):
    db_movie = db.query(database.Movie).filter(database.Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    for key, value in movie.model_dump().items():
        setattr(db_movie, key, value)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(database.get_db)):
    db_movie = db.query(database.Movie).filter(database.Movie.movieId == movie_id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    db.delete(db_movie)
    db.commit()
    return None

@app.get("/links", response_model=List[schemas.Link])
def get_links(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(database.Link).offset(skip).limit(limit).all()

@app.post("/links", response_model=schemas.Link, status_code=status.HTTP_201_CREATED)
def create_link(link: schemas.LinkCreate, db: Session = Depends(database.get_db)):
    db_link = db.query(database.Link).filter(database.Link.movieId == link.movieId).first()
    if db_link:
        raise HTTPException(status_code=400, detail="Link already exists")
    new_link = database.Link(**link.model_dump())
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@app.get("/links/{movie_id}", response_model=schemas.Link)
def get_link(movie_id: int, db: Session = Depends(database.get_db)):
    db_link = db.query(database.Link).filter(database.Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link

@app.put("/links/{movie_id}", response_model=schemas.Link)
def update_link(movie_id: int, link: schemas.LinkCreate, db: Session = Depends(database.get_db)):
    db_link = db.query(database.Link).filter(database.Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    
    for key, value in link.model_dump().items():
        setattr(db_link, key, value)
    
    db.commit()
    db.refresh(db_link)
    return db_link

@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(movie_id: int, db: Session = Depends(database.get_db)):
    db_link = db.query(database.Link).filter(database.Link.movieId == movie_id).first()
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(db_link)
    db.commit()
    return None

@app.get("/ratings", response_model=List[schemas.Rating])
def get_ratings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(database.Rating).offset(skip).limit(limit).all()

@app.post("/ratings", response_model=schemas.Rating, status_code=status.HTTP_201_CREATED)
def create_rating(rating: schemas.RatingCreate, db: Session = Depends(database.get_db)):
    new_rating = database.Rating(**rating.model_dump())
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating

@app.get("/ratings/{rating_id}", response_model=schemas.Rating)
def get_rating(rating_id: int, db: Session = Depends(database.get_db)):
    db_rating = db.query(database.Rating).filter(database.Rating.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@app.put("/ratings/{rating_id}", response_model=schemas.Rating)
def update_rating(rating_id: int, rating: schemas.RatingCreate, db: Session = Depends(database.get_db)):
    db_rating = db.query(database.Rating).filter(database.Rating.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    for key, value in rating.model_dump().items():
        setattr(db_rating, key, value)
    
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(rating_id: int, db: Session = Depends(database.get_db)):
    db_rating = db.query(database.Rating).filter(database.Rating.id == rating_id).first()
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    db.delete(db_rating)
    db.commit()
    return None

@app.get("/tags", response_model=List[schemas.Tag])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(database.Tag).offset(skip).limit(limit).all()

@app.post("/tags", response_model=schemas.Tag, status_code=status.HTTP_201_CREATED)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(database.get_db)):
    new_tag = database.Tag(**tag.model_dump())
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return new_tag

@app.get("/tags/{tag_id}", response_model=schemas.Tag)
def get_tag(tag_id: int, db: Session = Depends(database.get_db)):
    db_tag = db.query(database.Tag).filter(database.Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@app.put("/tags/{tag_id}", response_model=schemas.Tag)
def update_tag(tag_id: int, tag: schemas.TagCreate, db: Session = Depends(database.get_db)):
    db_tag = db.query(database.Tag).filter(database.Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)
    
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(database.get_db)):
    db_tag = db.query(database.Tag).filter(database.Tag.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(db_tag)
    db.commit()
    return None
