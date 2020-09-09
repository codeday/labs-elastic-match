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
from api.mentor import mentor_matches, retrieve_mentor_votes, save_mentor_choices
from api.student import save_student_choices
from random import randint, shuffle


class MentorTests(TestCase):
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

    def generate_student_votes_for_mentor(self, project_id: str, jwt_token: str):
        student_ids = ["rec6dPGkGcMtnYg02", "rec6kY5xQMKwbXBhd", "rec2i5KOFI1a144dR",
                       "rec288k49LFCx0hBg", "rec1nMv1Zul3JRCoU"]
        shuffle(student_ids)
        for student_id in student_ids:
            choice_data = encode(
                {
                    "student_id": student_id,
                    "votes": [
                        {"proj_id": project_id, "choice": randint(1, 3)},
                    ]
                },
                jwt_token,
            )
            yield choice_data

    def test_get_mentor_matches(self):
        with self.env:
            counter = 0
            for student_vote in self.generate_student_votes_for_mentor("recAmfKOaD2aXtpnB", self.jwt_token):
                response = save_student_choices(student_vote.decode('ascii'))
                self.assertEqual(response, '{"ok": true, "updated": 1}')
                counter += 1

            mentor_data = encode(
                {
                    "id": "recAmfKOaD2aXtpnB"
                },
                self.jwt_token,
            )

            # time.sleep(1)

            response = mentor_matches(mentor_data.decode("ascii"))
            self.assertIsNotNone(response)
            num_resp = len(loads(response)["students"])
            self.assertEqual(5, num_resp,
                             "The wrong number of students were matched with the mentor")

    # def test_student_votes(self):
    #     with self.env:
    #         choice_data = encode(
    #             {
    #                 "student_id": "rec03s7tmgmxVlDZu",
    #                 "votes": [
    #                     {"proj_id": "reczqDxIOXArZyOpx", "choice": 1},
    #                     {"proj_id": "recyVWYD3hUaEr5KO", "choice": 2},
    #                     {"proj_id": "recOeuRebe0SFd4Sw", "choice": 3},
    #                     {"proj_id": "recAmfKOaD2aXtpnB", "choice": 4},
    #                     {"proj_id": "recFtnrM4ZyO7lYBG", "choice": 5},
    #                 ]
    #             },
    #             self.jwt_token,
    #         )
    #
    #         response = save_student_choices(choice_data.decode('ascii'))
    #         self.assertIsNotNone(response, 200)
    #         self.assertEqual(loads(response)["updated"], 5, "Wrong number of student votes added")
    #
    #         time.sleep(0.5)
    #
    #         student_id = encode(
    #             {
    #                 "student_id": "rec03s7tmgmxVlDZu"
    #             },
    #             self.jwt_token,
    #         )
    #
    #         response = retrieve_student_votes(student_id.decode('ascii'))
    #         self.assertIsNotNone(response, 200)
    #         print(response)
