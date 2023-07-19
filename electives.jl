using CSV, DataFrames, CurricularAnalytics, CurricularAnalyticsDiff

prereq_df = DataFrame(CSV.File("./app/infrastructure/files/prereqs.csv"))

courses_from_prereqs = []
courses_from_curric = []

for row in eachrow(prereq_df)
    #println(row[:"Course ID"])
    if typeof(row[:"Prereq Sequence ID"]) != Missing
        push!(courses_from_prereqs, strip((row[:"Course Subject Code"])) * " " * strip((row[:"Course Number"])))
    end
end

courses_from_prereqs = Set(courses_from_prereqs)

big_curric = read_csv("./app/infrastructure/files/condensed2.csv")
courses_from_curric = Set(courses_to_course_names(big_curric.courses))

not_in_curric = setdiff(courses_from_prereqs, courses_from_curric)
not_in_prereqs = setdiff(courses_from_curric, courses_from_prereqs)

println("Not accounted for, but have prereqs:")
println(length(not_in_curric))
println(length(not_in_curric) / length(courses_from_prereqs) * 100)

println(sort(collect(courses_from_curric)))
