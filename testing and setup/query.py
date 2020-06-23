import requests
from jwt import encode
import uuid, random, json
import os

JWT_KEY = os.getenv("JWT_KEY")


def get_matches():
    student = {
        "id": str(uuid.uuid4()),
        "name": "TestTest",
        "rural": True,
        "underrepresented": False,
        # "timezone": random.randint(-7, -4),
        "timezone": -4,
        "interestCompanies": ['Microsoft', "Google"],
        "interestTags": ["Backend", "Data", "python", "php"],
        "requireExtended": False,
        "track": "Advanced"
    }

    data = encode(student, JWT_KEY).decode("utf-8")
    # r = requests.get("http://labs-elastic-match.codeday.cloud/matches/" + data)
    r = requests.get("http://localhost:9900/matches/" + data)
    json_data = json.loads(r.content.decode("utf-8"))
    print(str(student["timezone"]) + str([student["score"] for student in json.loads(r.content)]))


def store_student():
    data = {
        "student_id": "rec03s7tmgmxVlDZu",
        "votes": [
            {"proj_id": "recjcesxayRUS9kIH", "choice": 1},
            {"proj_id": "recfRVcYvECgJ0BlY", "choice": 2},
            {"proj_id": "recicI3vLpk1uPV3X", "choice": 3},
            {"proj_id": "recJnr93NhrWClUX2", "choice": 4},
            {"proj_id": "rec4PQBsmPrR3Eeiu", "choice": 5},
        ]
    }

    body = encode(data, JWT_KEY).decode("utf-8")
    print(body)
    # r = requests.put("http://labs-elastic-match.codeday.cloud/votes/" + body)
    r = requests.put("http://localhost:9900/votes/" + body)
    print(r.content)


def get_votes():
    data = {
        "student_id": "rec03s7tmgmxVlDZu"
    }

    body = encode(data, JWT_KEY).decode("utf-8")
    print(body)
    # r = requests.put("http://labs-elastic-match.codeday.cloud/votes/" + body)
    r = requests.get("http://localhost:9900/votes/" + body)
    print(r.content)


get_votes()