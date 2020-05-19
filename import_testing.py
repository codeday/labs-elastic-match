# Ensure that skip this and come back is false, for there is a lot of empty fields

from elasticsearch_dsl import connections
from models import Mentor, Project
from helpers import *

conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

mentor = Mentor(
    email="johnpeter@srnd.org",
    phone="(111) 111-1111",
    timezone=-8,  # America pacific is UTC-8
    two_projects=True,
    is_recruited_mentor=True,
    why_mentor="I like to mentor junior people and share what I've learned with them",
    past_mentoring="Been a TA in college",
    linkedin="https://www.example.com",
    company="SRND",
    where_work_text="Seattle WA",
    where_work_point="47.6062,-122.3321",
    # where_work_point=location_text_to_geopoint("Seattle WA"),
    role="Friendly Human",
    industry="Computers",
    experience=5,
    grow_up_text="In the Interwebs",
    grow_up_number=1,

    # Next section will define weights if possible
    student_specific_tool_experience=2,
    student_specific_tool_desire=1,
    student_similar_upbringing=0,
    student_similar_background=1,
    student_alma_mater=2,
    student_desire_company=1,
    student_underrepresented=0,
    student_continue_check_in_ok=2,
    student_timezone_outside_workday=1,

    # More personal information on mentor
    pronoun="they/them",
    ethnicity="Robot",
    can_commit=True,
    company_hour_matching=True,

    # These two should be yes
    signature_captured=True,
    entry_reviewed=True
)

mentor.save()


mentor.add_project(
    proposal="Build a contact tracing app using GPS for Android. Optionally, think of it as a proximity sensing application. If two apps are within meters of each other for an extended time then it logs it. If one of them contracts Covid-19 then this is logged.",
    tags=listify("Frontend, Web Dev, Data, HCI/UX, Backend")
    )

mentor.add_project(
    proposal="Restaurant Website with Angular and Bootstrap",
    tags=listify("Web Dev, Frontend")
)

