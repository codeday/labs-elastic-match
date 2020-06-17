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
