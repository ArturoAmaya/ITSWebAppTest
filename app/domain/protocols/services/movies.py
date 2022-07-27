from typing import List, Optional, Protocol


from app.domain.models.movie import Movie, MovieCreate, MovieRead, MovieReplace, MovieUpdate

class MoviesService(Protocol):

    async def get_movie(self, movieId: int) -> Optional[MovieRead]:
        ...

    async def list_movies(self) -> List[MovieRead]:
        ...
    
    async def create_movie(self, movie: MovieCreate) -> MovieRead:
        ...
    
    async def update_movie(self, movieId, movie: MovieUpdate) -> MovieRead:
        ...

    async def replace_movie(self, movieId, movie: MovieReplace) -> MovieRead:
        ...
    
    async def delete_movie(self, movieId) -> bool:
        ...
