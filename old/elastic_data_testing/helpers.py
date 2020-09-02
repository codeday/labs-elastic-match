"""
Assorted helper funcs for various data manipulation things, almost entirely unused since this was moved upstream. Keeping it around for now.
"""
import pytz, datetime
from pyzipcode import ZipCodeDatabase
from typing import Optional
import re


def zip_to_timeone(zipcode) -> int:  # zipcode: zipcode
    zcdb = ZipCodeDatabase()
    tz = zcdb[92078].timezone
    return tz


def parse_tz(tz_str: str) -> Optional[int]:
    """Parses the string forms of time zones from the data into ints"""
    if tz_str == 'America - Eastern':
        return -5
    if tz_str == 'America - Pacific':
        return -8
    if tz_str == 'America - Mountain':
        return -7
    if tz_str == 'America - Central':
        return -8
    if tz_str == 'America - Hawaii':
        return -10
    if tz_str == 'America - Atlantic':
        return -3
    else:
        return None


def fix_education_dict(dictionary) -> dict:
    """Fixes the education date ranges to be graduation year"""
    for k, v in dictionary.items():
        # If a year is givin in the format yyyy-yyyy, need to parse to work with elastic
        if re.match(r"[0-9]{4}-[0-9]{4}", v):
            dictionary[k] = v.split("-")[1]
    return dictionary


def parse_number(text):
    """Parses and cleans up some messy number fields"""
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


def fix_main_dict(dictionary) -> dict:
    """
    Fixes issues with strings of floats that cannot be directly cast to an int, and with bad booleans

    """
    for k, v in dictionary.items():
        if v == "Yes":
            dictionary[k] = True
        if v == "No":
            dictionary[k] = False
        if v == "1.0" or v == "2.0" or v == "3.0" or v == "0.00":
            dictionary[k] = int(float(v))
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


def listify(tags_str: str) -> list:
    """Takes a string list and makes it into a list.
        Now that I'm writing this docstring, this probably could have been a typecast...
    """
    return [i.strip() for i in tags_str.split(",")]


if __name__ == '__main__':
    print(zip_to_timeone(92078))
    print("Test")
