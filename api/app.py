import inspect
import os
import sys

from elasticsearch import Elasticsearch
from flask import Flask
from flask_restful import Api

# Long story short, imports bad.
# This is needed to allow the cogs to import database, as python doesn't check in the parent directory otherwise.
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

elastic_host = os.getenv("ELASTICSEARCH_URL")


app = Flask(__name__)
api = Api(app)
app.elasticsearch = Elasticsearch(elastic_host)
app.jwt_key = os.getenv("JWT_KEY")

from api.routes import GetMatches

api.add_resource(GetMatches, "/matches")


@app.route("/", methods=["GET"])
def index():
    return "TestTEstTEst"


if __name__ == '__main__':
    app.run(host="localhost", port=9900, debug=True)
