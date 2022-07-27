from typing import List, Optional

from fastapi import Depends
from sqlmodel import Session, select
from app.infrastructure.database.db import get_db
from app.domain.models.movie import Movie, MovieCreate, MovieRead, MovieReplace, MovieUpdate
from app.domain.protocols.repositories.movies import MoviesRepository as MoviesRepositoryProtocol


class MoviesRepository(MoviesRepositoryProtocol):
    ''' Provides data access to Movie models.
    
    The repository is an abstraction layer that defines the methods by which data can be accessed. They usualy return a single model, or a list of models of the same type.
    '''
    
    db: Session
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    async def get(self, id: int) -> Optional[Movie]:
        return self.db.get(Movie, id)
    
    async def list(self) -> List[Movie]:
        results = self.db.exec(select(Movie)).all()
        return results
    
    async def add(self, movie: MovieCreate) -> MovieRead:
        db_movie = Movie.from_orm(movie)
        self.db.add(db_movie)
        self.db.commit()
        self.db.refresh(db_movie)
        return db_movie
    
    async def update(self, id: int, movie: MovieUpdate) -> MovieRead:
        db_movie = await self.get(id)
        movie_data = movie.dict(exclude_unset=True) # Get just the values that were set
        for key, value in movie_data.items():
            setattr(db_movie, key, value)
        self.db.add(db_movie)
        self.db.commit()
        self.db.refresh(db_movie)
        return db_movie

    async def replace(self, id: int, movie: MovieReplace) -> MovieRead:
        db_movie = await self.get(id)
        movie_data = movie.dict() # Get just the values that were set
        for key, value in movie_data.items():
            setattr(db_movie, key, value)
        self.db.add(db_movie)
        self.db.commit()
        self.db.refresh(db_movie)
        return db_movie

    async def delete(self, id: int) -> bool:
        db_movie = await self.get(id)
        self.db.delete(db_movie)
        self.db.commit()
        return True