"""
Create fake testing data and load it into Elastic
"""

from elasticsearch_dsl import connections
from elastic.models import MentorProject
from uuid import uuid4
import random
from faker import Faker

fake = Faker()
conn = connections.create_connection(hosts=["10.0.3.33:9200"], timeout=20)


for i in range(40):
    mentor = MentorProject(
        id=uuid4(),
        name=fake.name(),
        company=fake.company(),
        bio=fake.paragraph(),
        backgroundRural=fake.pybool(),
        preferStudentUnderRep=random.randint(0, 2),  # (0-2)
        preferToolExistingKnowledge=fake.pybool(),
        okExtended=fake.pybool(),
        timezone=random.randint(-8, 4),
        proj_id=uuid4(),
        proj_description=fake.bs(),
        proj_tags=fake.words(),
        studentsSelected=0,
        okTimezoneDifference=fake.pybool(),
        isBeginner=False,
    )

    mentor.save()
