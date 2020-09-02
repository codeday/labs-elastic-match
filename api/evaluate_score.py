import elasticsearch_dsl
from elasticsearch import Elasticsearch
import uuid
import random
from elasticsearch_dsl import Q, SF
from elasticsearch_dsl.query import MatchNone, MatchAll
from json import dumps


# from typing import TypedDict, List

# Maybe typedDict isn't actually supported???
# class Student(TypedDict):
#     id: str
#     name: str
#     rural: bool
#     underrepresented: bool
#     requireExtended: bool
#     timezone: int
#     interestCompanies: List[str]
#     interestTags: List[str]
#     beginner: bool


def evaluate_score(student, client, num_resp: int = 25):
    """Takes a student, represented as a dictionary and an elasticsearch-py client and returns an elastic response

    See above student class for schema
    """

    # Adjust weights here:
    base_score = 1.0
    company_score = 1.0
    rural_score = 2.0
    tags_score = 3.0
    underrep_score = 1.0
    # Timezone weights are found in the timezone script query

    s = elasticsearch_dsl.Search(using=client, index="mentors_index").extra(
        explain=True
    )

    # Start by filtering the search by track
    s = s.filter("term", track=student["track"])

    # And also by requireExtended
    if student["requireExtended"]:
        s = s.filter("term", okExtended="true")

    if not student["underrepresented"]:
        s = s.exclude("term", preferStudentUnderRep=2)

    # Adds one to all remaining entries in order to be sure that, in the worst case,
    # there are enough responses, even if they aren't a good fit
    base_value = Q("constant_score", filter=MatchAll(), boost=base_score)

    # Uses a fuzzy query to determine if a student is interested in the mentor's company,
    # then if so adds `weight` to the score
    company_q = None
    for company in student["interestCompanies"]:
        if company_q is None:
            company_q = Q(
                "function_score",
                query=Q("fuzzy", company=company),
                weight=company_score,
                boost_mode="replace",
            )
        else:
            company_q = company_q | Q(
                "function_score",
                query=Q("fuzzy", company=company),
                weight=company_score,
                boost_mode="replace",
            )

    if student["rural"]:
        # If background_rural matches on mentor and student, then add one to the score
        background_rural = Q(
            "constant_score", filter=Q("term", backgroundRural=student["rural"]), boost=rural_score
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
                weight=tags_score / num_interests,
                boost_mode="replace",
            )
        else:
            tags_matching = tags_matching | Q(
                "function_score",
                query=Q("term", proj_tags=interest),
                weight=tags_score / num_interests,
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
    combined_query = Q("function_score", query=combined_query,
                       functions=SF("gauss", numStudentsSelected={"origin": 0, "scale": 3, "offset": 3, "decay": 0.50}))

    # Timezone - this one's a bit more complex. See comments in script for more details.
    # Multiplies it's value by the previous scores, allowing it to reduce, set to zero, and increase scores.
    # See below string for python implementation
    """
    if mentor['okTimezoneDifference']:
        if 16 < student['timezone'] < 22:
            return True
        return false
    else:
        if abs(student['timezone'] - mentor['timezone']) < 3:
            return True
        return False
    """


    s = s.query(combined_query)[0:num_resp]
    resp = s.execute()
    return resp


if __name__ == "__main__":

    # Out of date
    student = {
        "id": uuid.uuid4(),
        "name": 'John Peter',
        "rural": True,
        "underrepresented": True,
        "timezone": random.randint(-8, 4),
        "interestCompanies": ["Microsoft", "Google"],
        "interestTags": ["javascript", "java", "python", "php"],
        "requireExtended": True,
        "track": "Beginner",
    }
    client = Elasticsearch(hosts=["10.0.3.33:9200"])

    resp = evaluate_score(student, client)
    print("Done!")
