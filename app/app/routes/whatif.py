from http.client import HTTPException
from typing import Optional, List

from fastapi import APIRouter, Depends, Form, HTTPException, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# from app.domain.protocols.services.movies import MoviesService as MoviesServiceProtocol
from app.domain.services.movies import MoviesService
# from app.domain.models.movie import Movie, MovieCreate, MovieRead, MovieReplace, MovieUpdate

from fastapi_redis_session import getSessionStorage, SessionStorage
from app.domain.services.user import get_user_info

import json

# for julia
# escience center approach
# import julia
# from julia import Main
# from julia import Pkg
# Pkg.using('CurricularAnalytics')
# from julia import CurricularAnalytics
# julia.install()

# towards data science blog approach
from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import Main
jl.using("CurricularAnalytics")
jl.eval('include("./app/infrastructure/api_methods.jl")')
jl.eval('include("./app/infrastructure/api_server.jl")')

Main.eval('big_curric = read_csv("./app/infrastructure/files/condensed2.csv")')


router = APIRouter()
templates = Jinja2Templates(directory="app/app/templates")


# all routes except "/" are SSO-protected by intiailizing the session variable
# which checks for a login cookie
# this also depends on the sessionStorage variable being declared as a dependency to your routing function
@router.get("/", name="whatif:hello-world",response_class=HTMLResponse)
async def base_whatif(request: Request,sessionStorage: SessionStorage = Depends(getSessionStorage)):
    #movies = await movies_service.list_movies()
    #return templates.TemplateResponse("movies/list_movies.html", {"request": request, "movies": movies}) 
    
    return str(Main.eval('condensed.courses[1]'))

@router.get("/edit/add-course/", name="whatif:add-course",response_class=HTMLResponse)
async def add_course(request: Request, course: str, hours: float, prereqs, dependencies, nominal_plans, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    print(course, hours, prereqs, dependencies, nominal_plans)
    print(type(course), type(hours), type(prereqs), type(dependencies), type(nominal_plans))
    Main.course = course
    Main.hours = hours
    Main.prereqs = eval(prereqs)
    Main.dependencies = eval(dependencies)
    Main.eval("temp = Dict()")
    Main.eval("for (preq, type) in prereqs; if type==\"pre\"; temp[preq] = pre; end; end")
    Main.eval("prereqs = deepcopy(temp)")
    Main.eval("temp = Dict()")
    Main.eval("for (preq, type) in dependencies; if type==\"pre\"; temp[preq] = pre; end; end")
    Main.eval("dependencies = deepcopy(temp)")
    Main.eval('println("prereqs ", prereqs)')
    Main.eval('println("deps ", dependencies)') 
    Main.nominal_plans = eval(nominal_plans)
    Main.eval('results = add_course_inst_web(course, hours, prereqs, dependencies, read_csv("./app/infrastructure/files/condensed2.csv"), nominal_plans)')
    Main.eval('html_results = institutional_response_first_half * html_table(results) * institutional_response_second_half')
    return Main.html_results

@router.get("/edit/add-prereq/", name="whatif:add-prereq",response_class=HTMLResponse)
async def add_prereq(request: Request, course: str, prereq:str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.prereq = prereq
    Main.eval('results = add_prereq_inst_web(course, prereq)')
    Main.eval('html_results = institutional_response_first_half * html_table(results) * institutional_response_second_half')
    return Main.html_results

@router.get("/edit/remove-course/", name="whatif:remove-course",response_class=HTMLResponse)
async def remove_course(request: Request, course: str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.eval('results = remove_course_inst_web(course)')
    Main.eval('html_results = institutional_response_first_half * html_table(results) * institutional_response_second_half')
    return Main.html_results

@router.get("/edit/remove-prereq/", name="whatif:remove-prereq",response_class=HTMLResponse)
async def remove_prereq(request: Request, course: str, prereq:str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.prereq = prereq 
    Main.eval('results = remove_prereq_inst_web(course, prereq)')
    Main.eval('html_results = institutional_response_first_half * html_table(results) * institutional_response_second_half')
    return Main.html_results


