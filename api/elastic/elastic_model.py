"""
Houses the schema for the Elastic Database/
"""

from os import getenv

from elasticsearch_dsl import (
    Document,
    Text,
    Keyword,
    Boolean,
    Short,
    InnerDoc,
    Nested,
    Join,
    Integer,
    Object,
)
from elasticsearch import ConnectionPool


class StudentVote(InnerDoc):
    student_id = Keyword(required=True)
    choice = Integer()


class MentorProject(Document):
    name = Keyword(required=True)
    company = Text()
    bio = Text()
    backgroundRural = Boolean(required=True)
    preferStudentUnderRep = Short(required=True)  # (0-2)
    preferToolExistingKnowledge = Boolean(required=True)
    okExtended = Boolean(required=True)
    okTimezoneDifference = Boolean(required=True)
    timezone = Integer(required=True)  # +- UTC
    id = Keyword(required=True)
    proj_description = Text(required=True)
    proj_tags = Keyword(multi=True)
    numStudentsSelected = Short()
    listStudentsSelected = Nested(StudentVote)
    listMentorSelected = Keyword(multi=True)
    track = Keyword(required=True)

    class Index:
        name = getenv("MENTOR_INDEX_NAME", "mentor_index")
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    def save(self, **kwargs):
        self.numStudentsSelected = 0
        return super().save(**kwargs)


class StudentSchema(Document):
    """Ignored by elastic, is here for my refrence, may be implemented later"""

    id = Keyword(required=True)
    name = Keyword(required=True)
    rural = Boolean(required=True)
    underrepresented = Boolean(required=True)
    requireExtended = Boolean(required=True)
    timezone = Integer(required=True)
    interestCompanies = Keyword(multi=True, required=True)
    interestTags = Keyword(multi=True, required=True)


def make_db(host="10.0.3.33:9200"):
    from elasticsearch_dsl import connections

    connections.create_connection(hosts=[host], timeout=20)

    index_template = MentorProject._index.as_template("base")
    index_template.save()


def del_db(host="10.0.3.33:9200"):
    from elasticsearch_dsl import connections

    connections.create_connection(hosts=[host], timeout=20)

    something = MentorProject._index.delete()


if __name__ == "__main__":
    # del_db("mentor_index")
    make_db("10.0.3.33:9201")
