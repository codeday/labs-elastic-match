from flask import Flask
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from os import environ
import os, sys, inspect


# For JWT, use https://pyjwt.readthedocs.io/en/latest/api.html

# Long story short, imports bad.
# This is needed to allow the cogs to import database, as python doesn't check in the parent directory otherwise.
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

elastic_host = environ.get("ELASTICSEARCH_URL")

app = Flask(__name__)
api = Api(app)
app.elasticsearch = Elasticsearch(elastic_host) if elastic_host else None
app.jwt_key = "TESTTESTTEST"

from api.routes import GetMatches

api.add_resource(GetMatches, "/matches")


@app.route("/", methods=["GET"])
def index():
    return "TestTEstTEst"


if __name__ == '__main__':
    app.run(host="localhost", port=9900, debug=True)
