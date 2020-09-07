import inspect
import os
import sys

from elasticsearch import Elasticsearch
from flask import Flask

from elastic.evaluate_score import ScoreEvaluator

# Long story short, imports + directories bad.
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

elastic_host = os.getenv("ELASTICSEARCH_URL")
elastic_index = os.getenv("ELASTICSEARCH_INDEX", None)

app = Flask(__name__)
app.elasticsearch = Elasticsearch(elastic_host)
print(elastic_host)
app.scorer = ScoreEvaluator(index=elastic_index)
app.jwt_key = os.getenv("JWT_KEY")

import student
app.add_url_rule("/student/matches/<student_data>", methods=["GET"], view_func=student.student_matches)
app.add_url_rule("/student/votes/<choice_data>", methods=["PUT"], view_func=student.save_student_choices)
app.add_url_rule("/student/votes/<student_id>", methods=["GET"], view_func=student.retrieve_student_votes)

import mentor
app.add_url_rule("/mentor/matches/<mentor_data>", methods=["GET"], view_func=mentor.mentor_matches)
app.add_url_rule("/mentor/votes/<mentor_data>", methods=["PUT"], view_func=mentor.save_mentor_choices)
app.add_url_rule("/mentor/votes/<mentor_data>", methods=["GET"], view_func=mentor.retrieve_mentor_votes)


@app.route("/", methods=["GET"])
def main():
    return "Welcome to the ElasticMatch Webserver! There isn't anything useful here, go look around and find some other things!"


if __name__ == "__main__":
    app.run(host="localhost", port=9900, debug=True)
