from json import load
from elasticsearch_dsl import connections
from models import MentorProject
from faker import Faker

fake = Faker()

conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

with open("mentors.json", "r") as project_json_file:
    project_json = load(project_json_file)

    for project in project_json:
        project = MentorProject(
            id=project.get("mentor_id"),
            name=project.get("name"),
            company=project.get("company"),
            bio=project.get("bio"),
            backgroundRural=project.get("backgroundRural"),
            preferStudentUnderRep=project.get("preferStudentUnderRep"),
            preferToolExistingKnowledge=project.get("preferToolExistingKnowledge"),
            okExtended=project.get("okExtended"),
            okTimezoneDifference=fake.pybool(),
            timezone=project.get("timezone"),
            proj_id=project.get("proj_id"),
            proj_description=project.get("proj_description"),
            proj_tags=project.get("proj_tags"),
            track=project.get("track")
        )
        project.save()