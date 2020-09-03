from jwt import decode, exceptions
from werkzeug.exceptions import InternalServerError, Unauthorized
from flask import current_app
import json
from elasticsearch_dsl import UpdateByQuery, Search
from elasticsearch import RequestError


def unwrap_student_data(project_data_dict: dict) -> dict:
    unwrapped_dict = {}
    intermediate_list = []
    list_students = set([])
    for proj_id, project in project_data_dict.items():
        for student in project["listStudentsSelected"]:
            intermediate_list.append(
                {student["student_id"]: {proj_id: student["choice"]}}
            )
            list_students.add(student["student_id"])
    for student_id in list_students:
        unwrapped_dict[student_id] = {}
        for proj_data in intermediate_list:
            if list(proj_data.keys())[0] == student_id:
                unwrapped_dict[student_id][
                    list(proj_data[student_id].items())[0][0]
                ] = list(proj_data[student_id].items())[0][1]

    return unwrapped_dict


def mentor_matches(mentor_data):
    """
    Gives a list of students who voted for a mentor.
    TODO: Look into potential issue with ID being project not mentor level
    :param mentor_data: {
        "id": str(uuid.uuid4())
    }
    """

    try:
        data = decode(mentor_data, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")
    ela_resp = (
        Search(using=current_app.elasticsearch, index="mentors_index")
        .query("term", id=data["id"])
        .execute()
        .to_dict()
    )["hits"]["hits"][0]["_source"]
    resp = {
        "project_id": ela_resp["id"],
        "students": unwrap_student_data(ela_resp["listMentorSelected"]),
    }

    return json.dumps(resp)


def save_mentor_choices(choice_data):
    """
    :param choice_data: {
        "proj_id": "rec03s7tmgmxVlDZu",
        "votes": [
            {"student_id": "recjcesxayRUS9kIH", "choice": 1},
            {"student_id": "recfRVcYvECgJ0BlY", "choice": 2},
            {"student_id": "recicI3vLpk1uPV3X", "choice": 3},
            {"student_id": "recJnr93NhrWClUX2", "choice": 4},
            {"student_id": "rec4PQBsmPrR3Eeiu", "choice": 5},
            ...
        ]
    }
    """
    try:
        data = decode(choice_data, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")

    ubq_data = (
        UpdateByQuery(using=current_app.elasticsearch, index="mentors_index")
        .query("term", id=data["proj_id"])
        .script(
            source="ctx._source.listMentorSelected = newValue",
            params={
                "student": {"newValue": [vote["student_id"] for vote in data["votes"]]}
            },
        )
    )
    try:
        resp = ubq_data.execute().to_dict()
    except RequestError as e:
        raise InternalServerError(
            "Something went wrong with the update, please try again."
        )
    return json.dumps({"ok": True})


def retrieve_mentor_votes(project_id):
    """
    :param project_id: {
        "project_id": "rec03s7tmgmxVlDZu"
    }
    """
    try:
        data = decode(project_id, current_app.jwt_key, algorithms=["HS256"])
    except exceptions.DecodeError:
        raise Unauthorized("Something is wrong with your JWT Encoding.")
    ela_resp = (
        Search(using=current_app.elasticsearch, index="mentors_index")
        .query("term", id=data["id"])
        .execute()
        .to_dict()
    )["hits"]["hits"][0]["_source"]
    resp = {
        "project_id": ela_resp["id"],
        "mentor_votes": ela_resp["listMentorSelected"],
    }

    return json.dumps(resp)
