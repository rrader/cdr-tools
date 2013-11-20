from collections import namedtuple
import random

COUNTRIES = {"UA" : "380"}
CODES = ["000"]
PHONE_LENGTH = 12
NAMES = ["Jayne", "Cobb", "Kaylee", "Frye", "Hoban", "Wash", "Washburne", "Zoe", "Washburne", "Derrial", "Book",
         "River", "Tam", "Simon", "Tam", "Malcolm", "Reynolds", "Inara", "Serra"]

phonebook_entry = namedtuple("PhonebookEntry", ["name", "number"])


def phonebook_item_generator():
    """Generates unique phone number"""
    generated = []
    while True:
        number = generate_phone("UA", CODES[0])
        if number not in generated:
            generated.append(number)
            yield phonebook_entry(number=number, name="{} {}".format(random.choice(NAMES), random.choice(NAMES)))


def generate_phone(country, code):
    prefix = "{}{}".format(COUNTRIES[country], code)
    phone = "".join([str(random.randint(0, 9)) for _ in range(PHONE_LENGTH - len(prefix))])
    return "{}{}".format(prefix, phone)