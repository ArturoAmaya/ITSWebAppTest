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
new_plans = add_prereq_compound("MATH 109", "CHEM 6A", condensed, prereq_df, plans, new_plans)
new_condensed = condense_mem(plans, new_plans)
new_plans = add_prereq_compound("WCWP 10A", "CHEM 6A", new_condensed, prereq_df, plans, new_plans)
results = analyze_results(plans, new_plans)