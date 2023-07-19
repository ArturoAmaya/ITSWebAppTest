include("./api_methods.jl")
function mod_add_course_inst_web(course_name::AbstractString, credit_hours::Real, prereqs::Dict, dependencies::Dict, curr::Curriculum, nominal_plans::Vector{String})
    try
        df = DataFrame(CSV.File("./app/infrastructure/files/prereqs.csv"))
        results = Dict()
        # skip 0) the curric is passed in
        # get the list of affected plans
        affected = add_course_institutional(course_name, curr, credit_hours, prereqs, dependencies)
        plans = filter(x -> x != "", union!(nominal_plans, affected))
        # for each affected plan:
        for plan in plans
            major = plan[1:4]
            college = plan[5:end]
            try
                curr = read_csv("./app/infrastructure/files/output/$(major)/$(college).csv")
            catch
                println("$(major)$(college) plan not found")
                continue
            end
            if typeof(curr) == DegreePlan
                curr = curr.curriculum
            end
            try
                results[major]
            catch
                results[major] = Dict()
            end
            # add the course in. if all of its prereqs are there already, then it's all good
            # dependencies don't matter unless they happen to coincide with stuff already in the curriculum
            # add an empty course in
            new_curr = add_course(course_name, curr, credit_hours, Dict(), Dict())
            for (preq, type) in prereqs
                if preq in courses_to_course_names(curr.courses)
                    # hook up the prereq
                    println("all good with $preq in $major $college")
                    add_requisite!(course_from_name(preq, new_curr), course_from_name(course_name, new_curr), pre)
                else
                    # add the prereq
                    println("issue with $preq in $major $college -  add it in from the curriculum")
                    new_curr = add_dyno_prereq(course_name, preq, new_curr, df)
                end
            end
            # hook up the dependencies if they exist
            for (dep, type) in dependencies
                if dep in courses_to_course_names(new_curr.courses)
                    # hook up the dep
                    new_curr = add_prereq(dep, course_name, new_curr, pre)
                    #add_requisite!(course_from_name(course_name, new_curr), course_from_name(dep, new_curr), pre)
                end # else do nothing
            end
            ## don't run diff, just check the total credit hours and complexity scores 
            ch_diff = new_curr.credit_hours - curr.credit_hours
            complex_diff = complexity(new_curr)[1] - complexity(curr)[1] # consider using complexity(curr)
            new_curr_longest_path = length(longest_paths(new_curr)) > 0 ? length(longest_paths(new_curr)[1]) : 0
            old_curr_longest_path = length(longest_paths(curr)) > 0 ? length(longest_paths(curr)[1]) : 0
            path_change = new_curr_longest_path - old_curr_longest_path
            # write the results in 
            results[major][college] = Dict()
            results[major][college]["complexity"] = complex_diff
            results[major][college]["complexity %"] = (complex_diff / complexity(curr)[1]) * 100
            results[major][college]["unit change"] = ch_diff
            results[major][college]["new unit count"] = new_curr.credit_hours
            results[major][college]["longest path change"] = path_change
            results[major][college]["longest path change %"] = old_curr_longest_path == 0 ? 100 : path_change / old_curr_longest_path * 100
        end
        return (results, new_curr)
    catch e
        showerror(stdout, e)
        display(stacktrace(catch_backtrace()))
    end
end