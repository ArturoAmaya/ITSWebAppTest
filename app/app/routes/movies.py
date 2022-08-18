from http.client import HTTPException
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.domain.protocols.services.movies import MoviesService as MoviesServiceProtocol
from app.domain.services.movies import MoviesService
from app.domain.models.movie import Movie, MovieCreate, MovieRead, MovieReplace, MovieUpdate

from fastapi_redis_session import getSessionStorage, SessionStorage
from app.domain.services.user import get_user_info

router = APIRouter()
templates = Jinja2Templates(directory="app/app/templates")

# all routes except "/" are SSO-protected by intiailizing the session variable
# which checks for a login cookie
# this also depends on the sessionStorage variable being declared as a dependency to your routing function

@router.get("/", name="movies:get-movies",response_class=HTMLResponse)
async def list_movies(request: Request, movies_service = Depends(MoviesService), sessionStorage: SessionStorage = Depends(getSessionStorage)):
    movies = await movies_service.list_movies()
    return templates.TemplateResponse("movies/list_movies.html", {"request": request, "movies": movies}) 

@router.get("/add", name="movies:add-movie", response_class=HTMLResponse)
async def add_movies(request: Request):
    session = await get_user_info(request)

    return templates.TemplateResponse("movies/add_movie.html", {"request": request}) 

@router.get("/edit/{movieId}", name="movies:edit-movie",response_class=HTMLResponse)
async def edit_movie(request: Request, movieId: int, movies_service: MoviesServiceProtocol = Depends(MoviesService), sessionStorage: SessionStorage = Depends(getSessionStorage)):
    session = await get_user_info(request)

    movie = await movies_service.get_movie(movieId)
    return templates.TemplateResponse("movies/edit_movie.html", {"request": request, "movie": movie}) 

@router.get("/view/{movieId}", name="movies:get-movie", response_model=MovieRead)
async def get_movie_by_id(request: Request, movieId: int,  movies_service: MoviesServiceProtocol = Depends(MoviesService), sessionStorage: SessionStorage = Depends(getSessionStorage)) -> Optional[Movie]:
    session = await get_user_info(request)

    movie = await movies_service.get_movie(movieId)
    if not movie:
        raise HTTPException(404, "Movie not found")
    return templates.TemplateResponse("movies/view_movie.html", {"request": request, "movie": movie}) 

@router.post("/save", name="movies:save-movie", response_class=RedirectResponse)
async def save_movie(request: Request, 
                     id: Optional[int] = Form(None), 
                     title: str = Form(...), 
                     description: str = Form(...), 
                     year: int = Form(...), 
                     movies_service: MoviesServiceProtocol = Depends(MoviesService), 
                     sessionStorage: SessionStorage = Depends(getSessionStorage)) -> Movie:
    
    session = await get_user_info(request)
    
    if id:
        existingMovie = await movies_service.get_movie(id)
        if not existingMovie:
            raise HTTPException(404, "Existing movie not found.")
        
        newMovie = MovieReplace(title=title, description=description, movieYear=year)
        movie = await movies_service.replace_movie(id, newMovie)
    else:
        newMovie = MovieCreate(title=title, description=description, movieYear=year)
        movie = await movies_service.create_movie(newMovie)
    # TODO Figure out exceptions
    if not movie:
        raise HTTPException(400, "Unable to save movie.")
    
    url = request.url_for('movies:get-movie', movieId=movie.movieId)
    return RedirectResponse(url = url, status_code=302)

@router.post("/delete", name="movies:delete-movie", response_class=RedirectResponse)
async def delete_movie(request: Request, movieId: int = Form(...), movies_service: MoviesServiceProtocol = Depends(MoviesService), 
sessionStorage: SessionStorage = Depends(getSessionStorage)) -> Response:
    
    session = await get_user_info(request)

    movie = await movies_service.get_movie(movieId)
    
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    deleted = await movies_service.delete_movie(movieId)
    
    if not deleted:
        raise HTTPException(500, "The movie could not be deleted.")
    
    url = request.url_for('movies:get-movies')
    return RedirectResponse(url = url, status_code=302)
