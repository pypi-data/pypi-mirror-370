from mimesis import Person
from mimesis.locales import Locale
from mimesis.enums import Gender
import csv
import random
import faker
import io

fake = faker.Faker("en_US")


def create_van_record():
    if random.random() < 0.5:
        ln = Locale.EN
    else:
        ln = random.choice(list(Locale._member_map_.values()))
    person = Person(ln)

    gender = fake.random_choices([Gender.FEMALE, Gender.MALE], length=1)[0]

    return {
        "van_id": str(fake.random_int(100000, 9999999)),
        "first_name": person.first_name(gender),
        "last_name": person.last_name(gender),
        "phone_number": person.phone_number(mask="555#######"),
    }


def create_records(n):
    return [create_van_record() for _ in range(n)]
