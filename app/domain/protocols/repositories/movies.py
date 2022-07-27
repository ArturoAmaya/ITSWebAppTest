from typing import List, Optional, Protocol

from app.domain.models.movie import Movie, MovieCreate, MovieRead, MovieReplace, MovieUpdate

class MoviesRepository(Protocol):
    async def get(self, id: int) -> Optional[Movie]:
        ...
    
    async def list(self) -> List[Movie]:
        ...
    
    async def add(self, movie: MovieCreate) -> MovieRead:
        ...
    
    async def update(self, id: int, movie: MovieUpdate) -> MovieRead:
        ...

    async def replace(self, id: int, movie: MovieReplace) -> MovieRead:
        ...

    async def delete(self, id: int) -> bool:
        ...