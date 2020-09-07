import unittest
from api.elastic.elastic_model import make_db, del_db
from setup.elastic.json_import import load_file_to_index
from test.support import EnvironmentVarGuard
from api import app
import os
import time
from jwt import encode
import requests
from flask_testing import TestCase
from flask.wrappers import Response
from json import loads


class FlaskTests(TestCase):
    def create_app(self):
        app.app.config["TESTING"] = True
        app.app.config["DEBUG"] = False
        app.app.config["WTF_CSRF_ENABLED"] = False
        app.app.config["LIVESERVER_PORT"] = 9901
        return app.app

    def setUp(self) -> None:
        self.jwt_token = os.getenv("JWT_KEY")
        self.host = "10.0.3.33:9201"
        self.env = EnvironmentVarGuard()
        self.env.set("MENTOR_JSON_LOCATION", "../data/mentors-slim.json")

        with self.env:
            make_db(host=self.host)
            load_file_to_index(host=self.host)
            time.sleep(0.5)

    def tearDown(self) -> None:
        with self.env:
            del_db(host=self.host)

    def test_server_up_running(self):
        with self.env:
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)

    def test_student_matches_get(self):
        with self.env:
            student_data = encode(
                {
                    "id": "rec3cQopQfazDDQHp",
                    "name": "Kavin Manivasagam",
                    "rural": False,
                    "underrepresented": False,
                    "timezone": -5,
                    "interestCompanies": [
                        "Google",
                        "Facebook",
                        "Netflix",
                        "Adobe",
                        "Apple",
                        "Amazon",
                        "Microsoft",
                    ],
                    "interestTags": ["Mobile", "Backend", "Web Dev"],
                    "track": "Advanced",
                },
                self.jwt_token,
            )

            response: Response = self.client.get(
                f"/student/matches/{student_data.decode('ascii')}"
            )
            self.assertEqual(response.status_code, 200, "Student matches page did not respond")
            self.assertGreater(len(response.get_data()), 2, "Student matches page did not respond with enough "
                                                            "content, something probably failed")

    def test_student_votes(self):
        with self.env:
            choice_data = encode(
                {
                    "student_id": "rec03s7tmgmxVlDZu",
                    "votes": [
                        {"proj_id": "reczqDxIOXArZyOpx", "choice": 1},
                        {"proj_id": "recyVWYD3hUaEr5KO", "choice": 2},
                        {"proj_id": "recOeuRebe0SFd4Sw", "choice": 3},
                        {"proj_id": "recAmfKOaD2aXtpnB", "choice": 4},
                        {"proj_id": "recFtnrM4ZyO7lYBG", "choice": 5},
                    ]
                },
                self.jwt_token,
            )

            response = self.client.put(f"/student/votes/{choice_data.decode('ascii')}")
            self.assertEqual(response.status_code, 200, "Student vote PUT failed")
            self.assertEqual(loads(response.get_data().decode('ascii'))["updated"], 5,
                             "Wrong number of student votes added")

            print("Moving on to second half")
            time.sleep(0.5)

            student_id = encode(
                {
                    "student_id": "rec03s7tmgmxVlDZu"
                },
                self.jwt_token,
            )

            response = self.client.get(f"/student/votes/{student_id.decode('ascii')}")
            self.assertEqual(response.status_code, 200, "Student vote GET failed")
            print(response.get_data().decode('ascii'))

# TODO: Add tests for the mentor cases

if __name__ == "__main__":
    unittest.main()
