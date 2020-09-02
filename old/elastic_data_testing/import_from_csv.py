"""
Load mentor data from CSV. Obsolete since this was moved to JSON
"""

from elasticsearch_dsl import connections
from elastic.models import MentorProject
from helpers import *
from csv import DictReader

conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

with open("../older_schema/data/CodeLabs_Mentor_Application (1).xlsx - CodeLabsMentorApplication.csv", mode="r") as mentor_csv_file:
    mentor_dict = DictReader(mentor_csv_file)

    num_added_successfully = 0
    total_loops = 0

    for mentor_data in mentor_dict:
        total_loops += 1
        mentor_data = fix_main_dict(mentor_data)

        error_str = validate_entry(mentor_data)
        if error_str != "0":
            # TODO: Figure out how to really log this so we can come back, probably some logging file or something
            print("AHHHHHHHHHHHHH! This person's data is incomplete! I'm going to pass on adding this one, "
                  "but here's all the info I have on it. Please follow up! Also, the error code is: " + error_str)
            print(mentor_data)
            continue

        project_elastic = MentorProject(
            id=mentor_data["id"],
            name=mentor_data["name"],
            company=mentor_data["company"],
            bio=mentor_data["bio"],
            backgroundRural=mentor_data["backgroundRural"],
            preferStudentUnderRep=mentor_data["preferStudentUnderRep"],  # (0-2)
            preferToolExistingKnowledge=mentor_data["preferToolExistingKnowledge"],
            okExtended=mentor_data["okExtended"],
            timezone=mentor_data["timezone"],
            proj_id=mentor_data["proj_id"],
            proj_description=mentor_data["proj_description"],
            proj_tags=mentor_data["proj_tags"],
            studentsSelected=0,
            okTimezoneDifference=mentor_data["okTimezoneDifference"],
            isBeginner=mentor_data["isBeginner"],
        )

        project_elastic.save()

        num_added_successfully += 1
        # print(f"Another one down! So far, {num_added_successfully} out of {total_loops} have succeeded.")
