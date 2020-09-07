import elasticsearch_dsl
from elasticsearch import Elasticsearch
import uuid
import random
from elasticsearch_dsl import Q, SF
from elasticsearch_dsl.query import MatchNone, MatchAll


# This isn't currently supported in 3.7, however it helps to make things more clear for users
# from typing import TypedDict, List

# class Student(TypedDict):
#     id: str
#     name: str
#     rural: bool
#     underrepresented: bool
#     requireExtended: bool
#     timezone: int  # Not current used
#     interestCompanies: List[str]
#     interestTags: List[str]
#     beginner: bool


class ScoreEvaluator(object):
    def __init__(
        self,
        base_score=1.0,
        company_score=1.0,
        rural_score=2.0,
        tags_score=3.0,
        underrep_score=1.0,
        index="mentor_index"
    ):
        self.base_score = base_score
        self.company_score = company_score
        self.rural_score = rural_score
        self.tags_score = tags_score
        self.underrep_score = underrep_score
        self.index = index

    def evaluate_score_for_student(self, student, client, num_resp: int = 25):
        """Takes a student, represented as a dictionary and an elasticsearch-py client and returns an elastic response

        See above student class for schema
        """

        s = elasticsearch_dsl.Search(using=client, index=self.index).extra(
            explain=True
        )

        # Start by filtering the search by track
        s = s.filter("term", track=student["track"])

        # And also by requireExtended
        if student.get("requireExtended"):
            s = s.filter("term", okExtended="true")

        if not student.get("underrepresented"):
            s = s.exclude("term", preferStudentUnderRep=2)

        # Adds one to all remaining entries in order to be sure that, in the worst case,
        # there are enough responses, even if they aren't a good fit
        base_value = Q("constant_score", filter=MatchAll(), boost=self.base_score)

        # Uses a fuzzy query to determine if a student is interested in the mentor's company,
        # then if so adds `weight` to the score
        company_q = None
        for company in student["interestCompanies"]:
            if company_q is None:
                company_q = Q(
                    "function_score",
                    query=Q("fuzzy", company=company),
                    weight=self.company_score,
                    boost_mode="replace",
                )
            else:
                company_q = company_q | Q(
                    "function_score",
                    query=Q("fuzzy", company=company),
                    weight=self.company_score,
                    boost_mode="replace",
                )

        if student["rural"]:
            # If background_rural matches on mentor and student, then add one to the score
            background_rural = Q(
                "constant_score",
                filter=Q("term", backgroundRural=student["rural"]),
                boost=self.rural_score,
            )
        else:
            background_rural = Q("constant_score", filter=MatchNone())

        # Adds `weight` * the number of matching tags to score
        tags_matching = None
        num_interests = len(student["interestTags"])
        for interest in student["interestTags"]:
            if tags_matching is None:
                tags_matching = Q(
                    "function_score",
                    query=Q("term", proj_tags=interest),
                    weight=self.tags_score / num_interests,
                    boost_mode="replace",
                )
            else:
                tags_matching = tags_matching | Q(
                    "function_score",
                    query=Q("term", proj_tags=interest),
                    weight=self.tags_score / num_interests,
                    boost_mode="replace",
                )

        combined_query = (
            base_value
            | tags_matching
            | company_q
            | background_rural
            # | prefer_student_underrep
        )

        # Decay the combined score based on the number of students who already voted for that
        combined_query = Q(
            "function_score",
            query=combined_query,
            functions=SF(
                "gauss",
                numStudentsSelected={
                    "origin": 0,
                    "scale": 3,
                    "offset": 3,
                    "decay": 0.50,
                },
            ),
        )

        s = s.query(combined_query)[0:num_resp]
        resp = s.execute()
        return resp


if __name__ == "__main__":
    # Out of date
    student = {
        "id": uuid.uuid4(),
        "name": "John Peter",
        "rural": True,
        "underrepresented": True,
        "timezone": random.randint(-8, 4),
        "interestCompanies": ["Microsoft", "Google"],
        "interestTags": ["javascript", "java", "python", "php"],
        "requireExtended": True,
        "track": "Beginner",
    }

    client = Elasticsearch(hosts=["10.0.3.33:9200"])
    scorer = ScoreEvaluator()
    resp = scorer.evaluate_score_for_student(student, client)
    print("Done!")
