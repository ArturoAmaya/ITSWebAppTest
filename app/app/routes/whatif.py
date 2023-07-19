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

import json

def sort_results(results):
    mykeys = list(results.keys())
    mykeys.sort()
    sorted_results = {i: results[i] for i in mykeys}
    print(results.keys())
    for major in sorted_results:
        print(major)
        print(sorted_results[major])
        for college in sorted_results[major]:
            print(college)
            for stat in sorted_results[major][college]:
                print(stat)
                sorted_results[major][college][stat] = round(sorted_results[major][college][stat], 2)
    return sorted_results

def pad_results(sorted_results):
    for major in sorted_results:
        try:
            sorted_results[major]["FI"]
        except:
            sorted_results[major]["FI"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["RE"]
        except:
            sorted_results[major]["RE"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["MU"]
        except:
            sorted_results[major]["MU"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["WA"]
        except:
            sorted_results[major]["WA"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["SI"]
        except:
            sorted_results[major]["SI"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["SN"]
        except:
            sorted_results[major]["SN"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try: 
            sorted_results[major]["TH"] 
        except:
            sorted_results[major]["TH"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
        try:
            sorted_results[major]["curriculum"] 
        except:
            sorted_results[major]["curriculum"] = {"new unit count": "N/A", "complexity change":"N/A", "complexity change %": "N/A", "longest path change": "N/A", "longest path change %": "N/A", "unit change": "N/A"}
    return sorted_results
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
jl.eval('include("./app/infrastructure/UCSDspecific.jl")')


Main.eval('big_curric = read_csv("./app/infrastructure/files/condensed2.csv")')
Main.eval('condensed = read_csv("./app/infrastructure/files/condensed2.csv")')
Main.eval('prereq_df = DataFrame(CSV.File("./app/infrastructure/files/prereqs.csv"))')
Main.eval('plans = read_base()')
Main.eval('new_plans = Dict()')


 
router = APIRouter()
templates = Jinja2Templates(directory="app/app/templates")

 

# all routes except "/" are SSO-protected by intiailizing the session variable
# which checks for a login cookie 
# this also depends on the sessionStorage variable being declared as a dependency to your routing function
@router.get("/", name="whatif:main",response_class=HTMLResponse) 
async def base_whatif(request: Request,sessionStorage: SessionStorage = Depends(getSessionStorage)):
    return templates.TemplateResponse("whatif/index.html", {"request":request})

@router.get("/edit/compound-request/", name="whatif:compound", response_class=HTMLResponse)
async def compound_request(request: Request, commands, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    #print(criterias)
    #criterias = eval(criterias)
    #print(criterias[0])
    #return criterias
    print(commands) 
    commands = eval(commands)
    print("looping")
    first_step = True
    future_chain = False
    if len(commands) > 0:
        future_chain = True 
    #Main.eval("plans = read_base()")
    Main.eval('new_plans = Dict()') 
    Main.eval('new_condensed = condensed')
    for command in commands:
        Main.first_step = first_step
        Main.future_chain = future_chain
        #unpack
        match command['command']:
            case 'add-course':
                # add stuff
                print("add course")
                print(command['payload'])
                Main.course = command['payload']['course']
                Main.credit_hours = float(command['payload']['credit_hours'])
                Main.prereqs = command['payload']['prereqs']
                Main.dependencies = command['payload']['dependencies']
                Main.nominal_plans = command['payload']['nominal_plans']

                Main.prereqs = command['payload']['prereqs']
                Main.dependencies = command['payload']['dependencies']
                Main.eval("temp = Dict()")
                Main.eval("for (preq, type) in prereqs; if type==\"pre\"; temp[preq] = pre; end; end")
                Main.eval("prereqs = deepcopy(temp)") 
                Main.eval("temp = Dict()")
                Main.eval("for (preq, type) in dependencies; if type==\"pre\"; temp[preq] = pre; end; end")
                Main.eval("dependencies = deepcopy(temp)")
                Main.eval('println("prereqs ", prereqs)')
                Main.eval('println("deps ", dependencies)') 
                Main.nominal_plans = command['payload']['nominal_plans']
                
                Main.eval('println("$course, $(credit_hours), $prereqs, $dependencies, $(nominal_plans)")')

                Main.eval('new_plans = add_course_compound(course, credit_hours, prereqs, dependencies, new_condensed, nominal_plans, prereq_df, plans, new_plans)')
                Main.eval('new_condensed = condense_mem(plans, new_plans)')
            case 'remove-course': 
                # remove stuff
                print(command['payload']['course'])
                print("remove-course")
                Main.course = command['payload']['course']
                Main.eval('new_plans = remove_course_compound(course, new_condensed, plans, new_plans)')
                Main.eval('new_condensed = condense_mem(plans, new_plans)')
            case 'add-prereq': 
                # add prereq stuff
                print("add-prereq")
                print(command['payload']['course'])
                print(command['payload']['prereq'])
                Main.course = command['payload']['course']
                Main.prereq = command['payload']['prereq']
                Main.eval('new_plans = add_prereq_compound(course, prereq, new_condensed, prereq_df, plans, new_plans)')
                Main.eval('new_condensed = condense_mem(plans, new_plans)')
            case 'remove-prereq': 
                # remove prereq stuff
                print(command['payload']['course'])
                print(command['payload']['prereq'])
                print("remove-prereq")
                Main.course = command['payload']['course']
                Main.prereq = command['payload']['prereq']
                Main.eval('new_plans = remove_prereq_compound(course, prereq, new_condensed, plans, new_plans)')
                Main.eval('new_condensed = condense_mem(plans, new_plans)')
            case _:
                # default stuff  
                print("uhoh") 
        first_step = False
    Main.eval('results = analyze_results(plans, new_plans)')
    results = Main.results 
    sorted_results = sort_results(results) 
    sorted_results = pad_results(sorted_results)
    print(sorted_results) 
    return templates.TemplateResponse("whatif/results.html", {"request":request, "results":sorted_results})

@router.get("/edit/add-course/", name="whatif:add-course",response_class=HTMLResponse)
async def add_course(request: Request, course: str, credit_hours: float, prereqs, dependencies, nominal_plans, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    print(course, credit_hours, prereqs, dependencies, nominal_plans)
    print(type(course), type(credit_hours), type(prereqs), type(dependencies), type(nominal_plans)) 
    Main.course = course 
    Main.hours = credit_hours
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
    Main.eval('results = add_course_inst_web(course, hours, prereqs, dependencies, condensed, nominal_plans, plans, prereq_df)')
    results = Main.results 
    mykeys = list(results.keys()) 
    mykeys.sort()
    sorted_results = {i: results[i] for i in mykeys}
    print(results.keys()) 
    for major in sorted_results:
        print(major)
        print(sorted_results[major])
        for college in sorted_results[major]: 
            print(college)
            for stat in sorted_results[major][college]:
                print(stat) 
                sorted_results[major][college][stat] = round(sorted_results[major][college][stat], 2)
    print(type(sorted_results))
    sorted_results = pad_results(sorted_results)
    print(sorted_results)
    return templates.TemplateResponse("whatif/results.html", {"request":request, "results":sorted_results})

@router.get("/edit/add-prereq/", name="whatif:add-prereq",response_class=HTMLResponse)
async def add_prereq(request: Request, course: str, prereq:str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.prereq = prereq
    Main.eval('results = add_prereq_inst_web(course, prereq, condensed, prereq_df, plans)')
    results = Main.results
    sorted_results = sort_results(results) 
    sorted_results = pad_results(sorted_results)
    print(sorted_results)
    return templates.TemplateResponse("whatif/results.html", {"request":request, "results":sorted_results})

@router.get("/edit/remove-course/", name="whatif:remove-course",response_class=HTMLResponse)
async def remove_course(request: Request, course: str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.eval('results = remove_course_inst_web(course, condensed, plans)')
    Main.eval("println(results)")
    results = Main.results
    sorted_results = sort_results(results) 
    sorted_results = pad_results(sorted_results)
    return templates.TemplateResponse("whatif/results.html", {"request":request, "results":sorted_results})

@router.get("/edit/remove-prereq/", name="whatif:remove-prereq",response_class=HTMLResponse)
async def remove_prereq(request: Request, course: str, prereq:str, sessionStorage: SessionStorage = Depends(getSessionStorage)):
    Main.course = course
    Main.prereq = prereq
    Main.eval('results = remove_prereq_inst_web(course, prereq, condensed, plans)')
    results = Main.results
    sorted_results = sort_results(results) 
    sorted_results = pad_results(sorted_results)
    print(sorted_results)
    return templates.TemplateResponse("whatif/results.html", {"request":request, "results":sorted_results})


