using CurricularAnalytics, CurricularAnalyticsDiff, JSON

deps = Dict("MATH 10A" => pre,
    "MATH 10A /20A" => pre,
    "MATH 10A /MATH 20A" => pre,
    "MATH 10A/20A" => pre,
    "MATH 10A/20A/MGT 3" => pre,
    "MATH 10A/MATH 20A" => pre, "MATH 20A" => pre)
course = "MATH 3D"
hours = 4.0

results = Dict()

affected = add_course_institutional(course, read_csv("./app/infrastructure/files/condensed2.csv"), hours, Dict(), deps)
plans = filter(x -> x != "", affected)
for plan in plans
    major = plan[1:4]
    college = plan[5:end]
    try
        curr = read_csv("./app/infrastructure/files/output/$(major)/curriculum.csv")
        if typeof(curr) == DegreePlan
            curr = curr.curriculum
        end
        println("$(plan), $(curr.credit_hours)")

        base = curr.credit_hours
        if college == "RE"
            base += 84.0
        elseif college == "TH"
            base += 64.0
        elseif college == "FI"
            base += 72.0
        elseif college == "SI"
            base += 68.0
        elseif college == "SN"
            base += 56.0
        elseif college == "MU"
            base += 56.0
        elseif college == "WA"
            base += 48.0
        elseif college == "curriculum"
            continue
        end

        if base < 180
            if base + 8 > 180 || base + 12 > 180
                results["$(major) $(college)"] = Dict("base" => base, "With 2-course pre-calc" => base + 8, "With 3-course pre-calc" => base + 12)
            end
        end
    catch
        println("$(major)$(college) plan not found")
        continue
    end
end

open("results.json", "w") do f
    JSON.print(f, results)
end