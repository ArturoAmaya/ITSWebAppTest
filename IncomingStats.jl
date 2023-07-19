# This is to help analyze how many students need a particular course in a particular quarter.
using CurricularAnalytics, CurricularAnalyticsDiff


for (root, dirs, files) in walkdir("./app/infrastructure/files/output/")
    for file in files
        c = read_csv(joinpath(root, file))
        if typeof(c) == DegreePlan
            # do stuff here
            term = c.terms[1]
            courses = term.courses
            println(courses_to_course_names(courses))
        end
    end
end