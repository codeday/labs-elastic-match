# Ensure that skip this and come back is false, for there is a lot of empty fields

from elasticsearch_dsl import connections
from models import Mentor, Project

conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

mentor = Mentor(
    email = "johnpeter@srnd.org",
    phone = "(111) 111-1111",
    timezone = -8,  # America pacific is UTC-8
    two_projects = True,
    is_recruited_mentor = True,
    why_mentor = "I like to mentor junior people and share what I've learned with them",
    past_mentoring = "Been a TA in college",
    linkedin = "https://www.example.com",
    company = "SRND",
    where_work_text = "Seattle WA"
    where_work_point =
    role =
    industry =
    mentor_experience =
    grow_up_text =
    grow_up_number =

    # Next section will define weights if possible
    student_specific_tool_experience =
    student_specific_tool_desire =
    student_similar_upbringing =
    student_similar_background =
    student_alma_mater =
    student_desire_company =
    student_underrepresented =
    student_continue_check_in_ok =
    student_timezone_outside_workday =

    # More personal information on mentor
    pronoun =
    ethnicity =
    can_commit =
    company_hour_matching =

    # These two should be yes
    signature_captured = True,
    entry_reviewed = True
)

