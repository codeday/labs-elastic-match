from typing import Tuple
from copy import deepcopy


def count_lost_students(starting_students_count: int, project_data_dict: dict, placement_dict: dict) -> int:
    students = []
    for i in [[student for student in project["students"]] for k, project in placement_dict.items()]:
        for j in i:
            students.append(j)
    for i in [[student["student_id"] for student in project["listStudentsSelected"]] for k, project in
              project_data_dict.items()]:
        for j in i:
            students.append(j)
    return starting_students_count - len(set(students))


def find_lost_student_ids(starting_students_list: list, project_data_dict: dict, placement_dict: dict) -> list:
    students = []
    for i in [[student for student in project["students"]] for k, project in placement_dict.items()]:
        for j in i:
            students.append(j)
    for i in [[student["student_id"] for student in project["listStudentsSelected"]] for k, project in
              project_data_dict.items()]:
        for j in i:
            students.append(j)
    return list(set(starting_students_list) - set(students))


def unwrap_student_data(project_data_dict: dict) -> dict:
    unwrapped_dict = {}
    intermediate_list = []
    list_students = set([])
    for proj_id, project in project_data_dict.items():
        for student in project['listStudentsSelected']:
            intermediate_list.append({student["student_id"]: {proj_id: student["choice"]}})
            list_students.add(student["student_id"])
    for student_id in list_students:
        unwrapped_dict[student_id] = {}
        for proj_data in intermediate_list:
            if list(proj_data.keys())[0] == student_id:
                unwrapped_dict[student_id][list(proj_data[student_id].items())[0][0]] = \
                list(proj_data[student_id].items())[0][1]

    return unwrapped_dict


def measure_match_effectiveness(placement_dict: dict, unwrapped_student_dict: dict) -> int:
    score = 0

    for project_id, project in placement_dict.items():
        for student_id in project["students"]:
            score += unwrapped_student_dict[student_id][project_id]

    return score


def count_student_votes(project_data_dict: dict, student_id: str) -> int:
    student_votes = 0
    for k, project in project_data_dict.items():
        student_votes += len(
            [student for student in project['listStudentsSelected'] if student["student_id"] == student_id])
    return student_votes


def remove_student(project_data_dict: dict, student_id: str) -> dict:
    """Removes the provided student ID from the all_project_data dict"""
    for id, project in project_data_dict.items():
        project_data_dict[id]["listStudentsSelected"] = [
            student
            for student in project["listStudentsSelected"]
            if student["student_id"] != student_id
        ]
    return project_data_dict


def place_student(
        project_data_dict: dict, placement_dict: dict, project_id: str, student_id: str
) -> Tuple[dict, dict]:
    """Places the student in the project, handles removing the student from project data as well as decrementing
    needed students and placing needed info in placement_dict. Also removes completed projects from the project data and
    decrements "num_first_choice" if needed.

    :return project_data_dict, placement_dict
    """
    choice = 0
    for student in project_data_dict[project_id]["listStudentsSelected"]:
        if student["student_id"] == student_id:
            choice = student["choice"]

    placement_dict[project_id]["students"].append(student_id)
    project_data_dict = remove_student(project_data_dict, student_id)
    project_data_dict[project_id]["proj_size_remaining"] -= 1
    if choice == 1:
        project_data_dict[project_id]["num_first_choice"] -= 1

    if project_data_dict[project_id]["proj_size_remaining"] <= 0:
        del project_data_dict[project_id]

    return project_data_dict, placement_dict


def place_students_of_choice(
        project_data_dict: dict,
        placement_dict: dict,
        project_id: str,
        choice: int,
        num: int,
) -> Tuple[dict, dict]:
    """Will place the first `num` students of choice `choice` on a project, or will place until all students of `choice`
    have been placed. Chooses between valid students by picking those who appear the least frequently in other remaining
    votes."""

    counter = 0
    modified_project_data_dict = deepcopy(project_data_dict)
    for student in project_data_dict[project_id]["listStudentsSelected"]:
        if counter >= num:
            break
        if student["choice"] == choice:
            place_student(modified_project_data_dict, placement_dict, project_id, student["student_id"])
            counter += 1
            # print(f"added to {project_id} for a total of {counter}")
        if project_data_dict[project_id] is None:
            break
    return modified_project_data_dict, placement_dict


def place_students_of_choice_balanced(
        project_data_dict: dict,
        placement_dict: dict,
        project_id: str,
        choice: list,
        num: int,
) -> Tuple[dict, dict]:
    """Will place the first `num` students of choice `choice` on a project, or will place until all students of `choice`
    have been placed. Chooses between valid students by picking those who appear the least frequently in other remaining
    votes."""

    counter = 0
    matching_student_frequency = sorted(
        {student["student_id"]: count_student_votes(project_data_dict, student["student_id"])
         for student in project_data_dict[project_id]["listStudentsSelected"]
         if student["choice"] in choice}.items(), key=lambda x: x[1])
    for i in range(num):
        if i >= len(matching_student_frequency):
            break
        project_data_dict, placement_dict = place_student(project_data_dict, placement_dict, project_id,
                                                          matching_student_frequency[i][0])

    return project_data_dict, placement_dict
