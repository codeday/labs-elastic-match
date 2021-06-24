"""Build the combined data dictionary and the student placement dictionary"""
import json
import os
from helpers import *
from copy import deepcopy
import requests
import itertools
import csv

"""Fetch the project size data"""
project_size_data_query = """
query {
    labs {
        mentors(where: {inStatus: ACCEPTED}) {
            projects {
                status
                id
                maxStudents
            }
        }
    }
}
"""
resp =  requests.post(
    "https://graph.codeday.org/",
    json={ "query": project_size_data_query },
    headers={ "X-Labs-Authorization": f"Bearer {os.getenv('TOKEN')}" },
).json()
projects = list(itertools.chain(*(m["projects"] for m in resp["data"]["labs"]["mentors"])))
accepted_projects = list((p for p in projects if p["status"] == "ACCEPTED"))
print(f"Found {len(accepted_projects)} available projects")
project_size_dict = {p["id"]: p["maxStudents"] for p in accepted_projects}

def get_id_for_csv_entry(entry):
    return entry.split('-')[-1]

projects_reshaped = {}
students_username = {}
projects_shortname = {}

with open("./prefs.csv", "r", encoding="utf-8") as student_prefs:
    reader = csv.reader(student_prefs)
    for row in reader:
        if (row[0] == "student"):
            continue
        student = get_id_for_csv_entry(row[0])
        students_username[student] = row[0]
        for ind, choice in enumerate(row[1:]):
            project_id = get_id_for_csv_entry(choice)
            projects_shortname[project_id] = choice
            if not project_id in projects_reshaped:
                projects_reshaped[project_id] = {"listStudentsSelected": [], "id": project_id}
            projects_reshaped[project_id]["listStudentsSelected"].append({ "choice": ind + 1, "student_id": student })

project_docs = projects_reshaped.values()

all_project_data = {}
student_placements = {}
for project_doc in project_docs:
    id_ = project_doc["id"]
    proj_size = project_size_dict[id_]
    if proj_size == 0:
        continue
    all_project_data[id_] = project_doc
    all_project_data[id_]["proj_size_remaining"] = proj_size
    all_project_data[id_]["num_first_choice"] = len(
        [choice for choice in project_doc.get('listStudentsSelected') if choice["choice"] == 1])

    student_placements[id_] = {"students": [], "proj_capacity": project_size_dict[id_]}

unwrapped_student_data = unwrap_student_data(all_project_data)

starting_students = []
for i in [[student["student_id"] for student in project["listStudentsSelected"]] for k, project in
          all_project_data.items()]:
    for j in i:
        starting_students.append(j)
num_starting_students = len(set(starting_students))

# Do step 1
for id, project in all_project_data.items():
    if project["proj_size_remaining"] == project["num_first_choice"]:
        all_project_data, student_placements = place_students_of_choice(all_project_data, student_placements, id, 1,
                                                                        project["proj_size_remaining"])
print("Step 1")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print("------------")

# Do step 2
for id, project in all_project_data.items():
    if project["proj_size_remaining"] >= project["num_first_choice"]:
        # print("Project is smaller than first choice")
        all_project_data, student_placements = place_students_of_choice(all_project_data, student_placements, id, 1,
                                                                        project["proj_size_remaining"])
print("Step 2")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print("------------")

# Do step 3
_all_project_data = deepcopy(all_project_data)
for id, project in _all_project_data.items():
    if project["proj_size_remaining"] >= project["num_first_choice"]:
        all_project_data, student_placements = place_students_of_choice_balanced(all_project_data, student_placements,
                                                                                 id, [2, 15],
                                                                                 project["proj_size_remaining"])
print("Step 3")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print("------------")

# # Do step 4
_all_project_data = deepcopy(all_project_data)
for id, project in _all_project_data.items():
    all_project_data, student_placements = place_students_of_choice_balanced(all_project_data, student_placements, id,
                                                                             [1, 2], project["proj_size_remaining"])
print("Step 4")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print("------------")

for i in range(3, 16, 4):
    _all_project_data = deepcopy(all_project_data)
    for id, project in _all_project_data.items():
        if project["proj_size_remaining"] >= project["num_first_choice"]:
            # print(f"Project is smaller than {i} choice")
            all_project_data, student_placements = place_students_of_choice_balanced(all_project_data,
                                                                                     student_placements, id,
                                                                                     [i, i + 1, i + 2, i + 3],
                                                                                     project["proj_size_remaining"])
print("Step 4.5")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print("------------")

# Step 5 - Go through all missed projects?
_all_project_data = deepcopy(all_project_data)
for id, project in _all_project_data.items():
    if len(project["listStudentsSelected"]) > 0:
        all_project_data, student_placements = place_students_of_choice_balanced(all_project_data, student_placements,
                                                                                 id, list(range(1, 20)),
                                                                                 project["proj_size_remaining"])


print("Step 5")
print(count_lost_students(num_starting_students, all_project_data, student_placements))
print(f"Lost student IDs: {find_lost_student_ids(list(unwrapped_student_data.keys()), all_project_data, student_placements)}")
print("------------")


score = measure_match_effectiveness(student_placements, unwrapped_student_data)
print(f"This match score: {score}, or {score / num_starting_students} per student")

# Check for issues
count = 0
for id, project in all_project_data.items():
    if project["proj_size_remaining"] >= len(project["listStudentsSelected"]):
        count += project["proj_size_remaining"]
print("Unfilled Spots:" + str(count))

count = 0
for id, project in all_project_data.items():
    if len(project["listStudentsSelected"]) > 0:
        count += 1
        # count += len(project["listStudentsSelected"])
print("Students left over:" + str(count))

student_placement_file = open("./student_placement.json", "w")
json.dump(student_placements, student_placement_file)

def get_student_choice(student_id, project_id):
    return [s["choice"] for s in projects_reshaped[project_id]["listStudentsSelected"] if s["student_id"] == student_id][0]

with open("warnings.txt", "w") as warnings:
    with open("student_placement.csv", "w") as student_placement_csv:
        writer = csv.writer(student_placement_csv)
        for project, data in student_placements.items():
            project_shortname = projects_shortname[project]
            students = [{
                "shortname": students_username[s],
                "choice": get_student_choice(s, project),
            } for s in data["students"]]

            if (len(students) <= data["proj_capacity"]/3):
                warnings.write(f"! PROJECT {project_shortname} has {len(students)}/{data['proj_capacity']} students. Options:\n")
                warnings.writelines([
                    f"  - {students_username[s_opt['student_id']]} ({s_opt['choice']})\n"
                    for s_opt in projects_reshaped[project]["listStudentsSelected"]
                    if not s_opt['student_id'] in data["students"]
                ])

            for student in students:
                if (student["choice"] > 3):
                    warnings.write(f"? STUDENT {student['shortname']} got choice {student['choice']}\n")

            writer.writerow([
                f"{project_shortname}({len(students)}/{data['proj_capacity']})",
                *list([f"({s['choice']}){s['shortname']}" for s in students])
            ])
