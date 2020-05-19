def point_to_timeone(point) -> int:  # point: GeoPoint https://tinyurl.com/pkqn4be
    pass


def location_text_to_geopoint(place: str):  # -> GeoPoint https://tinyurl.com/pkqn4be
    pass


def point_to_urbanity(point) -> int:  # takes in geopoint, returns census urbanity measurement
    pass


def listify(tags_str: str) -> list:
    return [i.strip() for i in tags_str.split(",")]
