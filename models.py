from elasticsearch_dsl import (
    Document,
    Text,
    GeoPoint,
    Date,
    Integer,
    Keyword,
    Boolean,
    connections,
    Short,
    Index,
    InnerDoc,
    Nested,
    MetaField,
    Join
)


class Project(InnerDoc):
    id = Keyword(required=True)
    description = Text(required=True)
    tags = Keyword(multi=True, required=True)
    studentsSelected = Short()  # Should be 0-3
    mentor_project = Join(relations={"mentor": "project"})

    # https://github.com/elastic/elasticsearch-dsl-py/issues/95

    @property
    def mentor(self):
        # cache mentor self.meta
        # any attributes set on self would be interpretted as fields
        if 'mentor' not in self.meta:
            self.meta.mentor = Mentor.get(
                id=self.mentor_project.parent, index=self.meta.index)
        return self.meta.mentor

    def save(self, **kwargs):
        # set routing to parents id automatically
        self.meta.routing = self.mentor_project.parent
        return super(Project, self).save(**kwargs)


class MentorProject(Document):
    id = Keyword(required=True)
    name = Keyword(required=True)
    company = Keyword(required=True)
    bio = Text(required=True)
    backgroundRural = Boolean(required=True)
    preferStudentUnderRep = Short(required=True)  # (0-2)
    preferToolExistingKnowledge = Boolean(required=True)
    okExtended = Boolean(required=True)
    timezone = Short(required=True)  # +- UTC
    project_mentor = Join(relations={"project": "mentor"})


    # Nested project document, up to two should exist
    projects = Nested(Project)

    class Index:
        name = "mentors_index"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    def add_project(self, id, proposal: str, tags: list, num_students: int = 0, ):
        project = Project(
            # required make sure the answer is stored in the same shard
            _routing=self.meta.id,
            # since we don't have explicit index, ensure same index as self
            _index=self.meta.index,
            # set up the parent/child mapping
            mentor_project={'name': 'project', 'parent': self.meta.id},

            # Field values
            id=id,
            description=proposal,
            tags=tags,
            studentsSelected=num_students,
        )
        project.save()

    def save(self, **kwargs):
        self.project_mentor = "mentor"
        return super(Mentor, self).save(**kwargs)


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

    index_template = Mentor._index.as_template("base")
    index_template.save()

    # mentors = Index("mentors")
    #
    # mentors.document(Mentor)
    #
    # mentors.create()
    # mentors.save()
