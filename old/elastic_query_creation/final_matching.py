"""Build the combined data dictionary and the student placement dictionary"""
import json
from old.elastic_query_creation.helpers import *
from copy import deepcopy

project_docs = open("../../final_match/mentor_index_dump_2", "r", encoding="utf-8")
project_size_data = json.load(open("../../final_match/mentors_size_data.json", "r", encoding="utf-8"))
project_size_dict = {project["proj_id"]: project["proj_size_remaining"] for project in project_size_data}

all_project_data = {}
student_placements = {}
for line in project_docs:
    project_doc = json.loads(line)
    if project_doc["id"] == 'recRJGXhTr9lEq1tO':
        continue
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
print(unwrapped_student_data)

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

student_placement_file = open("../../final_match/student_placement.json", "w")
json.dump(student_placements, student_placement_file)


print("lol")
