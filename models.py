from elasticsearch_dsl import Document, Text, GeoPoint, Date, Integer, Keyword, Boolean, connections, Short, Index, \
    InnerDoc, Nested


class Project(InnerDoc):
    project_proposal = Text(required=True)  # This should be a searchable corpus of text, so Text it is
    project_tags = Keyword(multi=True,
                           required=True)  # This should be a list, so be sure to assign values to it as a list
    num_students_confirmed = Short()  # Should be 0-3
    # https://github.com/elastic/elasticsearch-dsl-py/issues/95


class Education(InnerDoc):
    type = Keyword()
    year = Date()
    institution = Keyword()
    majorminor = Text()


class Mentor(Document):
    email = Keyword(required=True)  # Keyword should be used since this is not a body of text
    phone = Keyword(
        required=True)  # Keyword should be used since this is not a body of text, seems better than number types
    timezone = Short()  # This will have a number relative to UTC
    two_projects = Boolean(required=True)  # True if this person agreed to run two groups
    is_recruited_mentor = Boolean(required=True)  # IDK what this means
    why_mentor = Text(required=True)  # Again, is freeform and non-structured
    past_mentoring = Keyword(multi=True)  # This should be a list, so be sure to assign values to it as a list
    linkedin = Keyword(required=True)
    company = Keyword()
    location_keyword = Keyword()  # The location that they said they worked
    # location_geo = GeoPoint()
    role = Keyword()
    industry = Keyword()
    experience = Integer()
    grow_up_text = Keyword()
    #grow_up_number = Short()  # Census num for region the person grew up in. 1-3 is urban, 4-6 is suburbs, 7-9 is rural. -1 on error, 0 outside US

    # Next section will define weights if possible, all 0-2
    student_specific_tool_experience = Short()  # How important already knowing tools is
    student_specific_tool_desire = Short()  # How important willingness to learn specific tools is 
    student_similar_upbringing = Short()  # How important a similar upbringing is - census number, others
    student_similar_background = Short()  # How important a student's background is
    student_alma_mater = Short()  # How important the student's alma matter matches
    student_desire_company = Short()  # How important a student's desire to work at a company is
    student_underrepresented = Short()  # How important it is that the student is from an underrepresented group
    student_continue_check_in_ok = Boolean()  # Are continued checkins ok after the event to get more credit?
    student_timezone_outside_workday = Boolean()  # Is it ok if time zones are too different

    # More personal information on mentor
    pronoun = Keyword()
    ethnicity = Keyword()
    can_commit = Boolean()
    company_hour_matching = Boolean()

    # These two should be True
    signature_captured = Boolean()
    entry_reviewed = Boolean()

    # Nested project document, up to two should exist
    projects = Nested(Project)

    # Nested education doc, 0-n can exist
    education = Nested(Education)

    def add_project(self, proposal: str, tags: list, num_students: int = 0):
        self.projects.append(
            Project(project_proposal=proposal, project_tags=tags, num_students_confirmed=num_students)
        )

    def add_education(self, type, year, institution, majorminor):
        self.education.append(
            Education(type=type, year=year, institution=institution, majorminor=majorminor)
        )

    class Index:
        name = 'mentors_index'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }


if __name__ == '__main__':
    from elasticsearch_dsl import connections

    connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

    index_template = Mentor._index.as_template('base')
    index_template.save()

    # mentors = Index("mentors")
    #
    # mentors.document(Mentor)
    #
    # mentors.create()
    # mentors.save()
