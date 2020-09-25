"""
Loads the mentors into Elastic database from a JSON file.
"""

from json import load
from elasticsearch_dsl import connections, Search
from elastic.elastic_model import MentorProject
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os


def load_file_to_index(host="10.0.3.33:9200"):
    conn = connections.create_connection(hosts=[host], timeout=20)

    mentors_json = os.getenv("MENTOR_JSON_LOCATION", "mentors.json")
    with open(mentors_json, "r", encoding="utf-8") as project_json_file:
        project_json = load(project_json_file, encoding="utf-8")

        # TODO: change this to a bulk query and force refresh to be true
        errors = []
        for project in project_json:
            try:
                saved_project = MentorProject(
                    name=project.get("name"),
                    company=project.get("company"),
                    bio=project.get("bio"),
                    backgroundRural=project.get("backgroundRural"),
                    preferStudentUnderRep=project.get("preferStudentUnderRep"),
                    preferToolExistingKnowledge=project.get(
                        "preferToolExistingKnowledge"
                    ),
                    okExtended=project.get("okExtended"),
                    okTimezoneDifference=project.get("okTimezoneDifference"),
                    timezone=project.get("timezone"),
                    id=project.get("proj_id"),
                    proj_description=project.get("proj_description"),
                    proj_tags=project.get("proj_tags"),
                    track=project.get("track"),
                )
                saved_project.save()
            except Exception as ex:
                errors.append(project["name"])

    if len(errors) != 0:
        print(errors)


def generate_student_votes(host="10.0.3.33:9200"):
    """Loads student votes, in the format generated in prep_student_data.py, into the database. """
    client = Elasticsearch(host)

    all_projects = (
        Search(using=client, index="mentor_index")
        .params(size=10000)
        .query()
        .execute()
        .to_dict()
    )["hits"]["hits"]

    updates = []
    ids = []
    with open("testing_student_votes.json") as student_votes_file:
        student_votes = load(student_votes_file)

    for project in all_projects:
        ids.append(project["_source"]["id"])
        update = {
            "_op_type": "update",
            "_index": "mentor_index",
            "_id": project["_id"],
            "doc": {
                "listStudentsSelected": {"student_id": "dfsfdsfsdfs", "choice": 1,}
            },
        }
        updates.append(update)
    print(ids)

    bulk(client=client, actions=updates)


if __name__ == "__main__":
    load_file_to_index(host="10.0.3.33:9201")
    generate_student_votes(host="10.0.3.33:9201")
