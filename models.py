from elasticsearch_dsl import (
    Document,
    Text,
    Keyword,
    Boolean,
    Short,
    InnerDoc,
    Nested,
    Join
)


class MentorProject(Document):
    id = Keyword(required=True)
    name = Keyword(required=True)
    company = Text(required=True)
    bio = Text(required=True)
    backgroundRural = Boolean(required=True)
    preferStudentUnderRep = Short(required=True)  # (0-2)
    preferToolExistingKnowledge = Boolean(required=True)
    okExtended = Boolean(required=True)
    timezone = Short(required=True)  # +- UTC
    proj_id = Keyword(required=True)
    proj_description = Text(required=True)
    proj_tags = Keyword(multi=True, required=True)
    studentsSelected = Short()
    isBeginner = Boolean(required=True)

    class Index:
        name = "mentors_index"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }


class StudentSchema(Document):
    """Ignored by elastic, is here for my refrence, may be implemented later"""
    id = Keyword(required=True)
    name = Keyword(required=True)
    rural = Boolean(required=True)
    underrepresented = Boolean(required=True)
    requireExtended = Boolean(required=True)
    timezone = Short(required=True)
    interestCompanies = Keyword(multi=True, required=True)
    interestTags = Keyword(multi=True, required=True)


if __name__ == "__main__":
    from elasticsearch_dsl import connections

    connections.create_connection(hosts=["10.0.3.33:9200"], timeout=20)

    index_template = MentorProject._index.as_template("base")
    index_template.save()

    # mentors = Index("mentors")
    #
    # mentors.document(Mentor)
    #
    # mentors.create()
    # mentors.save()
