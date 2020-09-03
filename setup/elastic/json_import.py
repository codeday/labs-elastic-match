"""
Loads the mentors into Elastic database from a JSON file.
"""

from json import load
from elasticsearch_dsl import connections
from elastic.elastic_model import MentorProject
import os

conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

with open("mentors.json", "r", encoding="utf-8") as project_json_file:
    project_json = load(project_json_file, encoding="utf-8")

    errors = []
    for project in project_json:
        try:
            saved_project = MentorProject(
                name=project.get("name"),
                company=project.get("company"),
                bio=project.get("bio"),
                backgroundRural=project.get("backgroundRural"),
                preferStudentUnderRep=project.get("preferStudentUnderRep"),
                preferToolExistingKnowledge=project.get("preferToolExistingKnowledge"),
                okExtended=project.get("okExtended"),
                okTimezoneDifference=project.get("okTimezoneDifference"),
                timezone=project.get("timezone"),
                id=project.get("proj_id"),
                proj_description=project.get("proj_description"),
                proj_tags=project.get("proj_tags"),
                track=project.get("track")
            )
            saved_project.save()
        except Exception as ex:
            errors.append(project["name"])

if len(errors) == 0:
    print("🥳🎉🥳 All mentors loaded! 🥳🎉🥳")
else:
    print(errors)