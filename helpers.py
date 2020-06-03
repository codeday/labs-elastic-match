import pytz, datetime
from pyzipcode import ZipCodeDatabase
from typing import Optional


def zip_to_timeone(zipcode) -> int:  # zipcode: zipcode
    zcdb = ZipCodeDatabase()
    tz = zcdb[92078].timezone
    return tz


def parse_tz(tz_str: str) -> Optional[int]:
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


def location_text_to_geopoint(place: str):  # -> GeoPoint https://tinyurl.com/pkqn4be | None
    pass


def point_to_urbanity(point) -> int:  # takes in geopoint, returns census urbanity measurement
    """
    NOT WORKING, LOWER PRIORITY

    Census num for region the person grew up in.

    1-3 is urban, 4-6 is suburbs, 7-9 is rural. -1 on error, 0 outside US

    :param point: A geopoint
    :return:
    """
    pass


def listify(tags_str: str) -> list:
    return [i.strip() for i in tags_str.split(",")]


if __name__ == '__main__':
    print(zip_to_timeone(92078))
    print("Test")
