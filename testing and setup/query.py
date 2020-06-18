import requests
from jwt import encode
import uuid, random, json


def get_matches():
    student = {
        "id": str(uuid.uuid4()),
        "name": "TestTest",
        "rural": True,
        "underrepresented": True,
        "timezone": random.randint(-8, 4),
        "interestCompanies": ['Microsoft', "Google"],
        "interestTags": ["javascript", "java", "python", "php"],
        "requireExtended": False
    }

    body = {
        "jwt_encoded_student": encode(student, "TESTTESTTEST")
    }
    print(body)
    r = requests.get("http://localhost:9900/matches", data=body)
    print(r.content)


def store_student():
    data = {
        "student_id": "rec03s7tmgmxVlDZu",
        "votes": [
            {"proj_id": "recNRlhAmOOUy32V3", "choice": 1},
            {"proj_id": "reclyXfRCjMAtSVn0", "choice": 2},
            {"proj_id": "recaMlxDylhMQKmjx", "choice": 3},
            {"proj_id": "recFpuV5Ryhi9KfzB", "choice": 4},
            {"proj_id": "recRJGXhTr9lEq1tO", "choice": 5},
        ]
    }

    body = {
        "jwt_encoded_store_data": encode(data, "TESTTESTTEST")
    }
    print(body)
    r = requests.post("http://localhost:9900/matches", data=body)
    print(r.content)


store_student()
