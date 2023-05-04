"""Generator test main.abo file"""

from datetime import date, datetime
import json
from faker import Faker
from random import randint

RECORDS_NUM = 111

fake = Faker("uk_UA")
ab = {}
for __ in range(RECORDS_NUM):
    record = ()
    for ___ in range(randint(1,3)):
        record += ( ("Phone", fake.phone_number()), )
    if randint(0,1):
        record += ( ("Birthday",
            datetime.fromordinal(randint(719528, 732677)).strftime(r"%d.%m.%Y")), )
    if randint(0,2) > 1:
        record += ( ("Address", fake.address()), )
    name = fake.name().replace("пан ", "").replace("пані ", "")
    ab[name] = record

with open("main.abo", "w") as fh:
    fh.write(json.dumps(ab, indent=2, ensure_ascii=False))
