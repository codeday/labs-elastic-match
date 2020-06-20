import matplotlib.pyplot as plt
import numpy as np
from json import load

plt.rcdefaults()
fig, ax = plt.subplots()

with open("students.json") as student_json_data:
    student_json = load(student_json_data)

    timezones = np.unique([student["timezone"] for student in student_json])
    print(timezones)