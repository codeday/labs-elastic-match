import elasticsearch_dsl
from elasticsearch import Elasticsearch
import uuid
from faker import Faker
import random
from elasticsearch_dsl import Q, SF
from elasticsearch_dsl.query import MatchNone, MatchAll
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
    s = elasticsearch_dsl.Search(using=client, index="mentors_index").extra(
        explain=True
    )

    # Adds one to all queries in order to be sure that, in the worst case,
    # there are enough responses, even if they aren't a good fit
    base_value = Q("constant_score", filter=MatchAll())

    # Uses a fuzzy query to determine if a student is interested in the mentor's company,
    # then if so adds `weight` to the score
    company_q = None
    for company in student["interestCompanies"]:
        if company_q is None:
            company_q = Q(
                "function_score",
                query=Q("fuzzy", company=company),
                weight="1",
                boost_mode="replace",
            )
        else:
            company_q = company_q | Q(
                "function_score",
                query=Q("fuzzy", company=company),
                weight="1",
                boost_mode="replace",
            )

    # If background_rural matches on mentor and student, then add one to the score
    background_rural = Q(
        "constant_score", filter=Q("term", backgroundRural=student["rural"])
    )

    # Adds `weight` * the number of matching tags to score
    tags_matching = None
    for interest in student["interestTags"]:
        if tags_matching is None:
            tags_matching = Q(
                "function_score",
                query=Q("term", proj_tags=interest),
                weight=1,
                boost_mode="replace",
            )
        else:
            tags_matching = tags_matching | Q(
                "function_score",
                query=Q("term", proj_tags=interest),
                weight=1,
                boost_mode="replace",
            )

    # If student is underrepresented, add the value of `prefer_student_underrep` * `factor` to the score
    if student["underrepresented"]:
        prefer_student_underrep = Q(
            {
                "function_score": {
                    "field_value_factor": {
                        "field": "preferStudentUnderRep",
                        "factor": 1,
                        "modifier": "none",
                        "missing": 0,
                    }
                }
            }
        )
    else:
        # Adds 0 to query if nothing is found
        prefer_student_underrep = Q("constant_score", filter=MatchNone())

    # Creates a query adding up all the previous scores,
    # with a requirement that the mentor is available for extended if the student needs it
    if student["requireExtended"]:
        requireExtended = Q("term", okExtended=True)
        combined_query = (
                                 base_value
                                 | tags_matching
                                 | company_q
                                 | background_rural
                                 | prefer_student_underrep
                         ) & requireExtended
    else:
        combined_query = (
                base_value
                | tags_matching
                | company_q
                | background_rural
                | prefer_student_underrep
        )

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
    combined_query = Q(
        "function_score",
        query=combined_query,
        functions=[
            SF(
                "script_score",
                script={
                    "source": """
    int student_tz = params.student_tz;
    int mentor_tz = 0;
    // Null check. Even though timezone is required, somehow some null rows snuck in and bamboozled me
    if (doc['timezone'].size() == 0) {
        mentor_tz = 0;
    } else {
        mentor_tz = (int)doc['timezone'].value;
    }
    int diff = student_tz - mentor_tz;
    
    boolean mentor_ok_tz_diff = false;
    if (doc['okTimezoneDifference'].size() == 0) {
        mentor_ok_tz_diff = false;
    } else {
        mentor_ok_tz_diff = doc['okTimezoneDifference'].value;
    }
    
    if (mentor_ok_tz_diff == true) {
        if (student_tz < 22) {
            if (student_tz > 16) {
                // Mentor is OK with the time difference and student has a large time difference
                return 1;
            }
        } else {
            // Mentor is ok with time difference and student has a normal time
            return 0.75;
        }
    } else {
        if (diff <= 3) {
            // Mentor is not ok with time difference and student has normal time
            return 1;
        } else {
            // Mentor is not ok with time difference and student has weird time
            return 0;
        }
    }
    """,
                    "params": {"student_tz": student["timezone"]},
                },
            )
        ],
        boost_mode="multiply",
        score_mode="sum",
    )

    s = s.query(combined_query)[0:num_resp]
    resp = s.execute()
    return resp


if __name__ == '__main__':
    fake = Faker()

    student = {
        "id": uuid.uuid4(),
        "name": fake.name(),
        "rural": True,
        "underrepresented": True,
        "timezone": random.randint(-8, 4),
        "interestCompanies": ["Microsoft", "Google", fake.company(), fake.company()],
        "interestTags": ["javascript", "java", "python", "php"],
        "requireExtended": False,
    }

    resp = evaluate_score(student)
    print("Done!")
