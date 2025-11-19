import csv
import os
from typing import List, Dict, Any

class Movie:
    def __init__(self, movieId: str, title: str, genres: str):
        self.movieId = movieId
        self.title = title
        self.genres = genres

class Link:
    def __init__(self, movieId: str, imdbId: str, tmdbId: str):
        self.movieId = movieId
        self.imdbId = imdbId
        self.tmdbId = tmdbId

class Rating:
    def __init__(self, userId: str, movieId: str, rating: str, timestamp: str):
        self.userId = userId
        self.movieId = movieId
        self.rating = rating
        self.timestamp = timestamp

class Tag:
    def __init__(self, userId: str, movieId: str, tag: str, timestamp: str):
        self.userId = userId
        self.movieId = movieId
        self.tag = tag
        self.timestamp = timestamp

def load_data(filename: str, model_class: Any) -> List[Dict[str, Any]]:
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    results = []
    if not os.path.exists(data_path):
        return results
        
    with open(data_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Create object instance
            obj = model_class(**row)
            # Serialize using __dict__
            results.append(obj.__dict__)
    return results
