"""
So! For this to work, I will need a list of student preferences, like this
student_preferences = {
    "A": ["X1", "X2"],
    "B": ["Y2", "X1"],
    "C": ["X1", "Y1"],
    "D": ["Y2", "Y1"],
}
and mentor prefs like this
mentor_project_preferences = {
    "X1": ["C", "A", "B"],
    "X2": ["C", "D", "B"],
    "Y1": ["B", "D", "A"],
    "Y2": ["A", "D", "B"]
}
mentor_project_capacities = {
    'X1': 1,
    'X2': 1,
    'Y1': 1,
    'Y2': 1
}
"""
from matching.games import HospitalResident
from json import load, dumps

with open("../data/testing_student_votes.json") as student_votes_fp:
    student_votes = load(student_votes_fp)

student_preferences = {
    student: [list(mentor.keys())[0] for mentor in votes]
    for student, votes in student_votes[0].items()
}
mentor_project_preferences = student_votes[1]
mentor_project_capacities = {mentor: 5 for mentor, student in student_votes[1].items()}

game = HospitalResident.create_from_dictionaries(
    student_preferences, mentor_project_preferences, mentor_project_capacities
)

game.solve(optimal="resident")
print(game.check_validity())
print(game.check_stability())
print(game.matching)

print(
    dumps(
        dict(
            zip(
                [mentor.name for mentor in game.matching.keys()],
                [
                    [student.name for student in mentor_match]
                    for mentor_match in game.matching.values()
                ],
            )
        )
    )
)
