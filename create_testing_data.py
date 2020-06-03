from elasticsearch_dsl import connections
from models import Mentor, Project
from uuid import uuid4
import random
from faker import Faker

fake = Faker()
conn = connections.create_connection(hosts=['10.0.3.33:9200'], timeout=20)

for i in range(40):
    mentor = Mentor(
        id=uuid4(),
        name=fake.name(),
        company=fake.company(),
        bio=fake.paragraph(),
        backgroundRural=fake.pybool(),
        preferStudentUnderRep=random.randint(0, 2),  # (0-2)
        preferToolExistingKnowledge=fake.pybool(),
        okExtended=fake.pybool(),
        timezone=random.randint(-8, 4)  # +- UTC
    )

    mentor.save()

    mentor.add_project(
        id=uuid4(),
        proposal=fake.bs(),
        tags=fake.words(),
        num_students=0
    )

    if fake.pybool():
        mentor.add_project(
            id=uuid4(),
            proposal=fake.bs(),
            tags=fake.words(),
            num_students=0
        )
