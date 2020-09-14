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

student_preferences = {
    "A": ["X1", "X2"],
    "B": ["Y2", "X1"],
    "C": ["X1", "Y1"],
    "D": ["Y2", "Y1"],
}
mentor_project_preferences = {
    "X1": ["C", "A", "B"],
    "X2": ["A"],
    "Y1": ["C", "D"],
    "Y2": ["B", "D"]
}
mentor_project_capacities = {
    'X1': 1,
    'X2': 1,
    'Y1': 1,
    'Y2': 1
}

game = HospitalResident.create_from_dictionaries(
    student_preferences, mentor_project_preferences, mentor_project_capacities
)

game.solve(optimal="resident")
print(game.check_validity())
print(game.check_stability())
print(game.matching)
