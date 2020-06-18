from flask_restful import Resource, reqparse
from flask import current_app
from api.evaluate_score import evaluate_score
from jwt import decode, exceptions
from werkzeug.exceptions import BadRequest
from elasticsearch_dsl import UpdateByQuery, Search
from elasticsearch.exceptions import RequestError

get_parser = reqparse.RequestParser()
get_parser.add_argument("jwt_encoded_student", dest="encoded_student", required=True)

post_parser = reqparse.RequestParser()
post_parser.add_argument("jwt_encoded_store_data", dest="encoded_data", required=True)


class GetMatches(Resource):
    def get(self):
        """Requires the python dict representation of a schema, see below for schema:
            class Student(TypedDict):
                id: str
                name: str
                rural: bool
                underrepresented: bool
                requireExtended: bool
                timezone: int
                interestCompanies: List[str]
                interestTags: List[str]
                beginner: bool
        """
        args = get_parser.parse_args()
        try:
            data = decode(
                args.encoded_student, current_app.jwt_key, algorithms=["HS256"]
            )
        except exceptions.DecodeError:
            raise BadRequest("Something is wrong with your JWT Encoding.")
        ela_resp = evaluate_score(data, current_app.elasticsearch, 25)
        resp = [
            {"score": hit._score, "project": hit._source.to_dict()}
            for hit in ela_resp.hits.hits
        ]
        return resp

    def post(self):
        """Requires some data, see schema below:

            jwt_encoded_store_data = {
                student_id: str,
                votes: [
                    {proj_id: str, choice: int},
                    ...
                ]
            }
        """
        args = post_parser.parse_args()
        try:
            data = decode(args.encoded_data, current_app.jwt_key, algorithms=["HS256"])
        except exceptions.DecodeError:
            raise BadRequest("Something is wrong with your JWT Encoding.")
        for vote in data["votes"]:
            ubq_data = (
                UpdateByQuery(using=current_app.elasticsearch, index="mentors_index")
                .query("term", proj_id=vote["proj_id"])
                .script(
                    source='if(!ctx._source.containsKey("listStudentsSelected")){ ctx._source.listStudentsSelected = new ArrayList();} ctx._source.listStudentsSelected.add(params.student);ctx._source.numStudentsSelected++;',
                    params={
                        "student": {
                            "student_id": data["student_id"],
                            "choice": vote["choice"],
                        }
                    },
                )
            )
            try:
                resp = ubq_data.execute()
            except RequestError as e:
                raise BadRequest(
                    "Something went wrong with the update, please try again."
                )
            else:
                return resp
