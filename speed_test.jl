include("./app/infrastructure/api_methods.jl")
condensed = read_csv("./app/infrastructure/files/condensed2.csv")
prereq_df = DataFrame(CSV.File("./app/infrastructure/files/prereqs.csv"))
plans = read_base()
new_plans = Dict()
#= 
new_plans = add_course_compound("MATH 30", 5.0, Dict(), Dict("MATH 20A" => pre, "MATH 10A" => pre), condensed, ["", "BI37RE"], prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
results = analyze_results(plans, new_plans)=#
# 533 seconds minimum time 


new_plans = add_course_compound("MATH 30", 5.0, Dict("MATH 20D" => pre), Dict("MATH 20E" => pre), condensed, ["", "BI37RE"], prereq_df, plans, new_plans)
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
println(results2)
# took 527.758s (1253117954 allocations: 40.65GiB)

# big speed test
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