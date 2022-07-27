from typing import List, Optional

from fastapi import Depends
from app.domain.protocols.repositories.movies import MoviesRepository as MoviesRepoProtocol
from app.domain.protocols.services.movies import MoviesService as MoviesServiceProtocol
from app.infrastructure.database.repositories.movies import MoviesRepository
from app.domain.models.movie import MovieCreate, MovieRead, MovieReplace, MovieUpdate

class MoviesService(MoviesServiceProtocol):
    '''
    Implements the business logic for dealing with movies. Services can do complex logic on multiple domain models, or just one.
    '''
    
    
    def __init__(self, movies_repo: MoviesRepoProtocol = Depends(MoviesRepository)):
        self.movies_repo = movies_repo

    async def get_movie(self, movieId: int) -> Optional[MovieRead]:
        return await self.movies_repo.get(movieId)

    async def list_movies(self) -> List[MovieRead]:
        return await self.movies_repo.list()
    
    async def create_movie(self, movie: MovieCreate) -> MovieRead:
        return await self.movies_repo.add(movie)
    
    async def update_movie(self, movieId, movie: MovieUpdate) -> MovieRead:
        return await self.movies_repo.update(movieId, movie)

    async def replace_movie(self, movieId, movie: MovieReplace) -> MovieRead:
        return await self.movies_repo.replace(movieId, movie)
    
    async def delete_movie(self, movieId) -> bool:
        return await self.movies_repo.delete(movieId)
