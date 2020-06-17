from flask_restful import Resource, reqparse
from flask import current_app
from api.evaluate_score import evaluate_score
from jwt import decode, exceptions
from werkzeug.exceptions import BadRequest


getMatches_parser = reqparse.RequestParser()
getMatches_parser.add_argument("jwt_encoded_student", dest="encoded_student", required=True)


class GetMatches(Resource):
    def get(self):
        args = getMatches_parser.parse_args()
        try:
            data = decode(args.encoded_student, current_app.jwt_key, algorithms=['HS256'])
        except exceptions.DecodeError:
            raise BadRequest("Something is wrong with your JWT Encoding.")
        ela_resp = evaluate_score(data, current_app.elasticsearch, 25)
        resp = [{"score": hit._score, "project": hit._source.to_dict()} for hit in ela_resp.hits.hits]
        return resp