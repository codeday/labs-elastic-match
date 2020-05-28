# Make sure to minimize the helper functions
# TODO: Move helpers to helpers.py (duh)

from elasticsearch_dsl import connections
from models import Mentor, Project
from helpers import *
from csv import DictReader
import re


def fix_bool(dictionary) -> dict:
    for k, v in dictionary.items():
        if v == "Yes":
            dictionary[k] = True
        if v == "No":
            dictionary[k] = False
    return dictionary


def validate_entry(dictionary: dict) -> str:
    """
    Checks to see if an entry has all the items it needs to have to be valid.

    This includes:
    * At least one full project
    * Skip this false
    * Signature true
    * Code of Conduct Agreement

    Some of this is required information, but I'm already writing the check to deal with lack of projects so :shrug:

    :param dictionary: The input dictionary, must be specifically the mentor dictionary
    :return: str of numbers. 0 if OK, otherwise the string will contain the following numbers if there is such an error:
     1 if no projects, 2 if skip this is true, 3 if no signature, 4 if code of conduct (i.e. "14" would mean no
     projects and no code of conduct.
    """
    error_str = ""

    if dictionary['FirstProjectProposal'] == "" or dictionary['TagThisProject'] == 'TagThisProject':
        error_str += "1"
    if dictionary['SkipThisAndComeBackToIt'] is True:
        error_str += "2"
    if dictionary['Signature'] != "Captured":
        error_str += "3"
    if dictionary['IAgreeToTheCodeOfConduct'] is not True:
        error_str += "4"
    if error_str == "":
        error_str = "0"
    return error_str


def parse_number(text):
    _pattern = r"""(?x)       # enable verbose mode (which ignores whitespace and comments)
        ^                     # start of the input
        [^\d+-\.]*            # prefixed junk
        (?P<number>           # capturing group for the whole number
            (?P<sign>[+-])?       # sign group (optional)
            (?P<integer_part>         # capturing group for the integer part
                \d{1,3}               # leading digits in an int with a thousands separator
                (?P<sep>              # capturing group for the thousands separator
                    [ ,.]                 # the allowed separator characters
                )
                \d{3}                 # exactly three digits after the separator
                (?:                   # non-capturing group
                    (?P=sep)              # the same separator again (a backreference)
                    \d{3}                 # exactly three more digits
                )*                    # repeated 0 or more times
            |                     # or
                \d+                   # simple integer (just digits with no separator)
            )?                    # integer part is optional, to allow numbers like ".5"
            (?P<decimal_part>     # capturing group for the decimal part of the number
                (?P<point>            # capturing group for the decimal point
                    (?(sep)               # conditional pattern, only tested if sep matched
                        (?!                   # a negative lookahead
                            (?P=sep)              # backreference to the separator
                        )
                    )
                    [.,]                  # the accepted decimal point characters
                )
                \d+                   # one or more digits after the decimal point
            )?                    # the whole decimal part is optional
        )
        [^\d]*                # suffixed junk
        $                     # end of the input
    """
    match = re.match(_pattern, text)
    if match is None or not (match.group("integer_part") or
                             match.group("decimal_part")):  # failed to match
        return None  # consider raising an exception instead

    num_str = match.group("number")  # get all of the number, without the junk
    sep = match.group("sep")
    if sep:
        num_str = num_str.replace(sep, "")  # remove thousands separators

    if match.group("decimal_part"):
        point = match.group("point")
        if point != ".":
            num_str = num_str.replace(point, ".")  # regularize the decimal point
        return float(num_str)

    return int(num_str)


conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

with open("./data/CodeLabs_Mentor_Application.csv", mode="r") as mentor_csv_file:
    mentor_csv_file_2 = open("./data/CodeLabs_Mentor_Application.xlsx - YourEducation.csv")
    mentor_dict = DictReader(mentor_csv_file)
    mentor_dict_2 = DictReader(mentor_csv_file_2)

    num_added_successfully = 0
    total_loops = 0

    for mentor_data in mentor_dict:
        total_loops += 1
        mentor_data = fix_bool(mentor_data)

        error_str = validate_entry(mentor_data)
        if error_str != "0":
            # TODO: Figure out how to really log this so we can come back, probably some logging file or something
            print("AHHHHHHHHHHHHH! This person's data is incomplete! I'm going to pass on adding this one, "
                  "but here's all the info I have on it. Please follow up! Also, the error code is: " + error_str)
            print(mentor_data)
            continue

        mentor_elastic = Mentor(
            email=mentor_data['Email'],
            phone=mentor_data['Phone'],
            timezone=-8,  # America pacific is UTC-8
            two_projects=mentor_data[
                'ByDefaultWeWillPickONEProjectProposalbasedOnStudentInterestIfYouWouldLikeToHostStudentGroupsForBOTHProjectsCheckThisBox'],
            is_recruited_mentor=mentor_data['IsRecruitedMentor'],
            why_mentor=mentor_data['WhyDoYouWantToVolunteer'],
            past_mentoring=mentor_data['Choice'],
            linkedin=mentor_data['LinkedInProfile'],
            company=mentor_data['Section_WhichCompanyDoYouWorkFor'],
            location_keyword=mentor_data['Section_WhereDoYouWork'],
            location_geo=location_text_to_geopoint('Section_WhereDoYouWork'),
            role=mentor_data['Section_WhatsYourRoleAtWork'],
            industry=mentor_data['Section_WhatTypeOfIndustryDoYouWorkIn'],
            experience=parse_number(mentor_data['Section_HowManyYearsOfExperienceDoYouHave']),
            grow_up_text=mentor_data['WhereDidYouGrowUp'],
            grow_up_number=point_to_urbanity(location_text_to_geopoint(mentor_data['WhereDidYouGrowUp'])),

            # Next section will define weights if possible
            student_specific_tool_experience=mentor_data['RatingScale_PreexistingExperienceWithTheToolsframeworkslanguagesIUse_Rating'],
            student_specific_tool_desire=mentor_data['RatingScale_DesireToLearnTheToolsframeworkslanguagesIUse_Rating'],
            student_similar_upbringing=mentor_data['RatingScale_SimilarUpbringingToMe_Rating'],
            student_similar_background=mentor_data['RatingScale_SimilarBackgroundToMe_Rating'],
            student_alma_mater=mentor_data['RatingScale_GoesTowantsToGoToMyAlmaMater_Rating'],
            student_desire_company=mentor_data['RatingScale_WantsToWorkForMyCompany_Rating'],
            student_underrepresented=mentor_data['RatingScale_IsAMemberOfAGroupUnderrepresentedInTechnology_Rating'],
            student_continue_check_in_ok=mentor_data['OkLengthyInternship'],
            student_timezone_outside_workday=mentor_data['OkTimezoneDifference'],

            # More personal information on mentor
            pronoun=mentor_data['Choice2'],
            ethnicity=mentor_data['WithWhichEthnicityDoYouMostIdentify'],
            can_commit=mentor_data['ICanCommitToMentorFromJuly631ForATotalTimeCommitmentOf20Hours'],
            company_hour_matching=mentor_data['DoesYourCompanyHaveAnHoursMatchingProgram'],

            # These two should be True
            signature_captured=mentor_data['Signature'],
            entry_reviewed=True,  # TODO: Understand what process happens with the status, see what the options are
        )

        mentor_elastic.save()

        mentor_elastic.add_project(
            proposal=mentor_data['FirstProjectProposal'],
            tags=listify(mentor_data['TagThisProject']),
        )

        if mentor_data['SecondProjectProposal'] is not None and mentor_data['TagThisProject2'] is not None:
            mentor_elastic.add_project(
                proposal=mentor_data['SecondProjectProposal'],
                tags=listify(mentor_data['TagThisProject2']),
            )

        mentor_elastic.save()
        num_added_successfully += 1
        print(f"Another one down! So far, {num_added_successfully} out of {total_loops} have succeeded.")
