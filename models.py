"""Houses the schema for the database and is used to create/update the index"""

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
    Object
)


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
    track = Keyword(required=True)

    class Index:
        name = "mentors_index"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    def add_vote(self, student_id, choice):
        self.listStudentsSelected.append(StudentVote(student_id=student_id, choice=choice))

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


if __name__ == "__main__":
    from elasticsearch_dsl import connections

    connections.create_connection(hosts=["10.0.3.33:9200"], timeout=20)

    index_template = MentorProject._index.as_template("base")
    index_template.save()