include("./app/infrastructure/api_methods.jl")
big_curric = read_csv("./app/infrastructure/files/condensed2.csv")
condensed = read_csv("./app/infrastructure/files/condensed2.csv")
prereq_df = DataFrame(CSV.File("./app/infrastructure/files/prereqs.csv"))
plans = read_base()
new_plans = Dict()

#= Test for adding MATH 109 and its '/' variations properly
new_plans = add_prereq_compound("MATH 109", "CHEM 6A", condensed, prereq_df, plans, new_plans)
=#

#= Test for adding CHEM 6A to MATH 109 then adding WCWP 10A to CHEM 6A.
    Initially treated as two separate adds - dps with math 109 should add 8 units (chem 6a and wcwp 10a), but those don't show up in the list
=#
#new_plans = add_prereq_compound("MATH 109", "CHEM 6A", condensed, prereq_df, plans, new_plans)
#new_condensed = condense_mem(plans, new_plans)
#new_plans = add_prereq_compound("CHEM 6A", "WCWP 10A", new_condensed, prereq_df, plans, new_plans)

# note that there's still the issue of when adding chem 6a to wcwp after adding chem 6a to math 109 that the field of edited plans
# shrinks to only the WA plans, which isn't true. this is the next issue to address:#
#=new_plans = add_prereq_compound("MATH 109", "CHEM 6A", condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = add_prereq_compound("WCWP 10A", "CHEM 6A", new_condensed, prereq_df, plans, new_plans)
results = analyze_results(plans, new_plans)=#

# try adding then removing a prereq to see what happens
#=new_plans = add_prereq_compound("MATH 109", "CHEM 6A", condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = add_prereq_compound("MATH 109", "CHEM 6A", new_condensed, prereq_df, plans, new_plans)
results = analyze_results(plans, new_plans)
println(results)
for major in keys(results)
    for college in keys(results[major])
        try
            println("$major $college complex ^: $(results[major][college]["complexity change %"]), new units: $(results[major][college]["new unit count"])")
        catch
            println("$major $college DNE")
        end
    end
end=#

# add a class then delete it
#=
new_plans = add_course_compound("MATH 30", 5.0, Dict("MATH 20A" => pre), Dict("MATH 20B" => pre), condensed, [""], prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = add_prereq_compound("MATH 30", "MATH 10A", new_condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = remove_course_compound("MATH 30", new_condensed, plans, new_plans)
results = analyze_results(plans, new_plans)
println(results)

new_plans2 = Dict()
new_plans2 = add_course_compound("MATH 30", 5.0, Dict("MATH 20A" => pre, "MATH 10A" => pre), Dict("MATH 20B" => pre), condensed, [""], prereq_df, plans, new_plans2)
new_condensed2 = condense_mem(plans, new_plans2)
new_plans2 = remove_course_compound("MATH 30", new_condensed2, plans, new_plans2)
results2 = analyze_results(plans, new_plans2)
println(results2)
=#

# add a class to specific unrelated majors then delete it
#=new_plans = add_course_compound("MATH 30", 5.0, Dict("MATH 20D" => pre), Dict("MATH 20E" => pre), condensed, ["", "BI37RE"], prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = add_prereq_compound("MATH 30", "CSE 11", new_condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = remove_course_compound("MATH 30", new_condensed, plans, new_plans)
results = analyze_results(plans, new_plans)
println(results)

new_plans2 = Dict()
new_plans2 = add_course_compound("MATH 30", 5.0, Dict("MATH 20D" => pre, "CSE 11" => pre), Dict("MATH 20E" => pre), condensed, ["", "BI37RE"], prereq_df, plans, new_plans2)
new_condensed2 = condense_mem(plans, new_plans2)
new_plans2 = remove_course_compound("MATH 30", new_condensed2, plans, new_plans2)
results2 = analyze_results(plans, new_plans2)
println(results2)=#
# the result here is that we add 16 units - MATH 20B, MATH 20C, MATH 20D and CSE 11. The issue is that 10B is already there. isn't that a vliad prereq? Apaprently not! this is good news!
# it uses the canonical choice of MATH 10B/MATH 20B being MATH 10B, which is not a prereq for 20C, so it has to add that in with 20B having 10B as a prereq.
# importantly the added course is gone
# TODO: consider having an option to delete it's tree up to a certain point.

#=
Next test:
Add a class pre-20A
=#
#=new_plans = add_course_compound("MATH 30", 5.0, Dict(), Dict("MATH 20A" => pre, "MATH 10A" => pre), condensed, ["", "BI37RE"], prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
results = analyze_results(plans, new_plans)
println(results)=#
# all good here

#=
Add a prereq then remove it, check that things are unaltered, and the same as add remove add remove
=#
new_plans = add_prereq_compound("MATH 20D", "CHEM 6A", condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = remove_prereq_compound("MATH 20D", "CHEM 6A", new_condensed, plans, new_plans)
results = analyze_results(plans, new_plans)
println(results)

new_plans2 = Dict()
new_plans2 = add_prereq_compound("MATH 20D", "CHEM 6A", condensed, prereq_df, plans, new_plans2)
new_condensed2 = condense_mem(plans, new_plans2)
new_plans2 = remove_prereq_compound("MATH 20D", "CHEM 6A", new_condensed2, plans, new_plans2)
results2 = analyze_results(plans, new_plans2)
new_plans2 = add_prereq_compound("MATH 20D", "CHEM 6A", new_condensed2, prereq_df, plans, new_plans2)
new_condensed2 = condense_mem(plans, new_plans2)
new_plans2 = remove_prereq_compound("MATH 20D", "CHEM 6A", new_condensed2, plans, new_plans)
results2 = analyze_results(plans, new_plans2)
println(results2)

issue = false
# diff the results 
#if sort(collect(keys(plans))) != sort(collect(keys(new_plans)))
#    print("yikes")
#else
for major in keys(new_plans)
    if (sort(collect(keys(plans[major]))) == sort(collect(keys(new_plans[major])))) && !issue
        for college in keys(plans[major])
            diff = curricular_diff(plans[major][college], new_plans[major][college])
            if diff["explained"]["complexity"] != 0.0 || diff["explained"]["centrality"] != 0.0 || diff["explained"]["blocking factor"] != 0.0 || diff["explained"]["delay factor"] != 0.0
                println("issue with explained in $major $college")
                issue = true
            end
            if diff["to explain"]["complexity"] != 0.0 || diff["to explain"]["centrality"] != 0.0 || diff["to explain"]["blocking factor"] != 0.0 || diff["to explain"]["delay factor"] != 0.0
                println("issue with to explain in $major $college")
                issue = true
            end
            if length(diff["unmatched courses"]) != 0
                println("issue with unmatched courses in $major $college")
                issue = true
            end
        end
    else
        break
    end
end
println(issue)