import random
import json

from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch

"""
Need to get to 
[
    {
        "student1": [{"mentor1": 1}, {"mentor2": 2}],
        "student1": [{"mentor4": 1}, {"mentor1": 2}],
        "student1": [{"mentor1": 1}, {"mentor3": 2}],
        "student1": [{"mentor4": 1}, {"mentor3": 2}]
    },
    {
    // Lists of students are not really ordered since they should be randomized before use to give all student a fair 
    // shot at being ranked
        "mentor1": ["student1", "student2", "student3"],
        "mentor2": ["student1"],
        "mentor3": ["student1", "student2", "student3"],
        "mentor4": ["student1", "student2", "student3"]
    }
]
Generates testing_student_votes.json with that format
"""


def getKey(_dict: dict) -> str:
    return list(_dict.keys())[0]


def generate_data(students, mentors, size):
    votes = {}

    for student in students:
        random.shuffle(mentors)
        selected_mentors = random.choices(mentors, k=size)
        votes[student] = []
        for i, mentor in enumerate(selected_mentors):
            votes[student].append({mentor: i+1})

    return votes


def rotate_data(data):
    """Takes a list of students and what they voted for and returns the mentors, and the students who voted for them"""
    unwrapped_dict = {}
    intermediate_list = []
    list_mentors = set([])
    for student, mentors in data.items():
        for mentor in mentors:
            mentor_id = getKey(mentor)
            intermediate_list.append({mentor_id: student})
            # [{mentor_id, student_id},{mentor_id, student_id},{mentor_id, student_id},{mentor_id, student_id},...]
            
            list_mentors.add(mentor_id)  # Just a list of all students

    for count, mentor_id in enumerate(list_mentors):
        unwrapped_dict[mentor_id] = []
        for pair in intermediate_list:
            if getKey(pair) == mentor_id:
                unwrapped_dict[mentor_id].append(list(pair.values())[0])

    return unwrapped_dict


if __name__ == "__main__":
    student_preferences_query = (
        Search(using=Elasticsearch("10.0.3.33:9201"), index="mentor_index")
        .params(size=10000)
        .query()
        .execute()
        .to_dict()
    )

    students = [
        "recPCAktSuaUkrPBC",
        "reczENHeqFTigzPUz",
        "recjqlGmiXVRWhtqa",
        "recjozEforMPGyyKG",
        "recMdWQsiWNIGOTbK",
        "recehYugFmaJGeAgE",
        "reccJfoyrixDyHGKK",
        "recaadNzgULTrUZKJ",
        "recTEUzfaBawSWZRL",
        "recWgFtTPBIhAxunC",
        "recXFkGpQrueEqGwF",
        "recZdwmxuZJbbqOfV",
        "recIPpuvzUsDfQbZR",
        "recsMqPqykqbYuwla",
        "recDQWhpRUallCItJ",
        "recnDeuaVekKYxdII",
        "reclREKRMmrFYWvGu",
        "recdoOecnKbgraalS",
        "recSxsuGLZsVVqAJY",
        "receYjlalpaRGGUsS",
        "recLwMhjyHYoILlFU",
        "recQYECMsasctTMNS",
        "recbmHCSYyBVjepXJ",
        "recTcRzzZCyxNOSJP",
        "receosJiNBuRnFezW",
        "recRYVjcGLgRFEKrQ",
        "recCJVZzIvZMEWuxH",
        "recWWmlzPDpnMNWLi",
        "reclBtwsLcmlxOjMX",
        "recMBUvnKBMeJDtkU",
        "recAkKWVyBWLNLyWs",
        "recBclYFIhsJUlCtQ",
        "recTxWPNfphYWBKeJ",
        "recsDjTRfBfRzCVqR",
        "recMzrlVRDAYzOHUQ",
        "recmerQwLTacRyMOA",
        "reckcBCyqpeRqnllL",
        "recWKqfmLtdIGdaeg",
        "recfchRaucopNeQKH",
        "recQGDvMOVtzcvvgw",
        "recyczWARqyQlwCbN",
        "recIVIZDSIPaImJWe",
        "recZbICQotAKREBhg",
        "reczsNeBngqocjDDl",
        "recrnuttGXNRMsKDO",
        "recBdYKauvYVjTiws",
        "recLTSjYifCRBJUZw",
        "reckWQbefqevUHWwN",
        "recSgqccdvTOUSLir",
        "recwNzalTDIyWdVuN",
        "recuhxvUvVWbdkCqI",
        "recdHLVWJKlLpLdRj",
        "recUkvUXjdhLceGgj",
        "recFMvQZnBiamhcIt",
        "recCuQhFzfeoIEVXL",
        "recSfZIhZJrdVwxWS",
        "recwgUpfgBNNhAShd",
        "recdKmjHiewRXdkSg",
        "rechEuHNBIYHlbxWS",
        "reciUmkufpNJiPWwP",
        "recJUwHPSgJaITTvM",
        "recIjPnybXBzbRroz",
        "recbkcUFTPOJxehbo",
        "recwZmFSKgznvNaQU",
        "recYVjQImQLUQcLfc",
        "recCRZiHvkGlgkXuH",
        "recIAhscHMeoQNyxw",
        "recjTctxANnNhZTCS",
        "reczTrUDeVCWqmhEJ",
        "recohQBIAWIqtEpYd",
        "recsxHrURyGOefxVQ",
        "recyeRmqCXKzYioBY",
        "recWylzbcdEcQZPpg",
        "recGiJxDsVWZEfbKs",
        "recPSTICNbCPWLBcm",
        "recwntGkidCiYQRAj",
        "recvUtuZkJhQmtxhe",
        "reckNPDGgnblDcasg",
        "reczmVVdUQHxUJqDn",
        "recwxQVxmCjxymLAy",
        "recolJWopUVibGhJU",
        "recKayNWTZwcEnAcG",
        "recmhnPrDFtoiKOcF",
        "recunPIACynAtOAwR",
        "recisYuYdbGNPBZjk",
        "recCCPIiVWEQrLhxF",
        "recGNjmUUOoAcEhHp",
        "recXOerDXYObREfpN",
        "recENxDQTWVeGthhw",
        "recKKqnVGDCUzAHty",
        "recgmrwZjfIxgYuWd",
        "recropeaTGqYHNZWq",
        "recPHwbrKQZpsHWSZ",
        "recbLDFJnQeOgLFpu",
        "recKimlBfjuqMXLwJ",
        "recVKdbmRgFEuRlxe",
        "recmuaGOYGzkHKukZ",
        "recGPGiOVpNPlgtUg",
        "recIQCbJcMCxQuZch",
        "recBkmrMmGRJDcKMT",
    ]

    mentors = [hit["_source"]["id"] for hit in student_preferences_query["hits"]["hits"]]

    votes = generate_data(students, mentors, 5)

    mentor_votes = rotate_data(votes)

    with open("../data/testing_student_votes.json", "w") as file:
        json.dump([votes, mentor_votes], file)

    print("fin")
