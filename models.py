from elasticsearch_dsl import Document, Text, GeoPoint, Date, Integer, Keyword, Boolean, connections, Short


class Mentor(Document):
    email = Keyword(required=True)  # Keyword should be used since this is not a body of text
    phone = Keyword(required=True)  # Keyword should be used since this is not a body of text, seems better than number types
    timezone = Short()  # This will have a number relative to UTC
    project_1_proposal = Text(required=True)  # This should be a searchable corpus of text, so Text it is
    project_1_tags = Keyword(multi=True, required=True)  # This should be a list, so be sure to assign values to it as a list
    # https://github.com/elastic/elasticsearch-dsl-py/issues/95
    project_2_proposal = (Text())  # This should be a searchable corpus of text, so Text it is
    project_2_tags = Keyword(multi=True)  # This should be a list, so be sure to assign values to it as a list
    one_or_both = Boolean(required=True)
    is_recruited_mentor = Boolean(required=True)
    why_mentor = Text(required=True)  # Again, is freeform and non-structured
    past_mentoring = Keyword(multi=True)  # This should be a list, so be sure to assign values to it as a list
    linkedin = Keyword(required=True)
    company = Keyword()
    where_work_text = Keyword()
    where_work_point = GeoPoint()
    role = Keyword()
    industry = Keyword()
    mentor_experience = Integer()
    grow_up_text = Keyword()
    grow_up_number = Short()  # Census num for region the person grew up in. 1-3 is urban, 4-6 is suburbs, 7-9 is rural
    
    # Next section will define weights if possible
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

    # These two should be yes
    signature_captured = Boolean()
    entry_reviewed = Boolean()


def setup():
    """
    Create the index in elastic, not really sure how this template bit works and how it differs from my above setup,
    however it was in the most similar example.
    """

    # create an index template, not really sure what this does?
    index_template = Mentor._index.as_template("base")
    # upload the template into elasticsearch
    # potentially overriding the one already there
    index_template.save()

    # Create the index
    if not Mentor._index.exists():
        Mentor.init()
