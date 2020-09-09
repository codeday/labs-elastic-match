from jwt import decode, exceptions
from werkzeug.exceptions import InternalServerError, Unauthorized
from flask import current_app
import json
from elasticsearch_dsl import UpdateByQuery, Search
from elasticsearch import RequestError
from elasticsearch.exceptions import ConflictError
import time


def student_matches(student_data):
    """
    :param student_data: {
        "id": str(uuid.uuid4()),
        "name": "TestTest",
        "rural": True,
        "underrepresented": False,
        "timezone": -4,
        "interestCompanies": ['Microsoft', "Google"],
        "interestTags": ["Backend", "Data", "python", "php"],
        "requireExtended": False,
        "track": "Advanced"
    }
    """
    try:
        data = decode(student_data, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")
    ela_resp = current_app.scorer.evaluate_score_for_student(
        data, current_app.elasticsearch, 25
    )
    resp = [
        {"score": hit._score, "project": hit._source.to_dict()}
        for hit in ela_resp.hits.hits
    ]
    return json.dumps(resp)


def save_student_choices(choice_data):
    """
    :param choice_data: {
        "student_id": "rec03s7tmgmxVlDZu",
        "votes": [
            {"proj_id": "recjcesxayRUS9kIH", "choice": 1},
            {"proj_id": "recfRVcYvECgJ0BlY", "choice": 2},
            {"proj_id": "recicI3vLpk1uPV3X", "choice": 3},
            {"proj_id": "recJnr93NhrWClUX2", "choice": 4},
            {"proj_id": "rec4PQBsmPrR3Eeiu", "choice": 5},
        ]
    }

    It turns out that the UpdateByQuery function does not support waiting for the index to refresh for some reason.
    We will have to find a way to work around that.
    """
    try:
        data = decode(choice_data, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")
    resps = []
    for vote in data["votes"]:
        s_res = (
            Search(using=current_app.elasticsearch, index="mentor_index")
            .query("term", id=vote["proj_id"])
            .execute()
        )

        u_res = current_app.elasticsearch.update(
            index="mentor_index",
            id=s_res["hits"]["hits"][0]["_id"],
            body={
                "script": {
                    "source": """if(!ctx._source.containsKey("listStudentsSelected")){ 
                                     ctx._source.listStudentsSelected = new ArrayList();
                                 } 
                                 ctx._source.listStudentsSelected.add(params.student);
                                 ctx._source.numStudentsSelected++;""",
                    "params": {
                        "student": {
                            "student_id": data["student_id"],
                            "choice": vote["choice"],
                        }
                    },
                }
            },
            refresh="true",
        )

        try:
            resps.append(u_res)
        except RequestError as e:
            raise InternalServerError(
                "Something went wrong with the update, please try again."
            )

    num_updated = sum([1 for resp in resps if resp["result"] == "updated"])
    return json.dumps({"ok": True, "updated": num_updated})


def retrieve_student_votes(student_id):
    """
    :param student_id: {
        "student_id": "rec03s7tmgmxVlDZu"
    }
    """
    try:
        data = decode(student_id, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")
    resp = current_app.elasticsearch.search(
        index="mentor_index",
        body={
            "query": {
                "nested": {
                    "path": "listStudentsSelected",
                    "query": {
                        "bool": {
                            "must": {
                                "term": {
                                    "listStudentsSelected.student_id": data[
                                        "student_id"
                                    ]
                                }
                            }
                        }
                    },
                }
            }
        },
    )

    # It was powerful, but alas too good for this world...
    # clean_resp.append([{"project_id": project["_source"]["id"], "choice": choice["choice"]} for choice in project["_source"]["listStudentsSelected"] if choice['student_id'] == data["student_id"]])
    clean_resp = []
    for project in resp["hits"]["hits"]:
        for choice in project["_source"]["listStudentsSelected"]:
            if choice["student_id"] == data["student_id"]:
                clean_resp.append(
                    {"project": project["_source"], "choice": choice["choice"]}
                )
    return json.dumps(clean_resp)
