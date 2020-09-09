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
        # shuffle(student_ids)
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

            response = mentor_matches(mentor_data.decode("ascii"))
            self.assertIsNotNone(response)
            num_resp = len(loads(response)["students"])
            self.assertEqual(5, num_resp,
                             "The wrong number of students were matched with the mentor")
            return response

    def test_save_mentor_matches(self):
        with self.env:
            student_votes = loads(self.test_get_mentor_matches())
            student_votes["proj_id"] = student_votes.pop("project_id")
            student_votes["votes"] = student_votes.pop("students")

            student_votes = encode(
                student_votes,
                self.jwt_token,
            )

            resp = save_mentor_choices(student_votes)
            self.assertEqual(resp, '{"ok": true}')

    def test_retrieve_mentor_votes(self):
        with self.env:
            self.test_save_mentor_matches()

            time.sleep(1)

            mentor_data = encode(
                {
                    "id": "recAmfKOaD2aXtpnB"
                },
                self.jwt_token,
            )
            resp = loads(retrieve_mentor_votes(mentor_data))
            self.assertEqual(len(resp['mentor_votes']), 5)
            self.assertEqual(resp['mentor_votes'][0], 'rec6dPGkGcMtnYg02')
            self.assertEqual(resp['mentor_votes'][1], 'rec6kY5xQMKwbXBhd')
            self.assertEqual(resp['mentor_votes'][2], 'rec2i5KOFI1a144dR')
            self.assertEqual(resp['mentor_votes'][3], 'rec288k49LFCx0hBg')
            self.assertEqual(resp['mentor_votes'][4], 'rec1nMv1Zul3JRCoU')

            print(resp)
