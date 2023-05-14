"""Class Phone

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


import re

from notabene.field import Field


class PhoneException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class Phone(Field):
    # Common pattern for each object
    pattern_phone_number = re.compile(
            r"(?:\+\d{1,3})?\s*(?:\(\d{2,5}\)|\d{2,5})?"
            r"\s*\d{1,3}(?:\s*-)?\s*\d{1,3}(?:\s*-)?\s*\d{1,3}")

    def __init__(self, phone=""):
        super().__init__(value=phone, title="Phone", order=30)
        if phone != "":
            self.value = phone # to validate non epmpty phone number

    @staticmethod
    def normalize_phone(phone: str) -> str:
        # Removing start/end spaces and change many spaces with one
        phone = " ".join(str(phone).split())
        phone = phone.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
        return phone

    @staticmethod
    def get_digits_from_str(text: str) -> str:
        return "".join(filter(str.isdigit, text))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, phone):
        phone = self.normalize(phone)
        self.verify(phone)
        # Phone number is proven and can be stored
        self._value = phone

    def verify(self, phone: str):
        """Check phone format"""
        m = Phone.pattern_phone_number.search(phone)
        if not bool(m):
            raise PhoneException(f"incorrect number '{phone}'")
        if m.start() != 0:
            raise PhoneException(f"extra symbol(s) '{phone[:m.start()]}' in the start")
        if m.end() != len(phone):
            raise PhoneException(f"extra symbol(s) '{phone[m.end():]}' in the end")
        if sum(map(lambda x: x.isdigit(), phone)) < 5:
            raise PhoneException(f"number '{phone}' is very short to be correct")
        # Phone number is proven
        return

    def __eq__(self, phone):
        if self.get_digits_from_str(str(self)) \
                == self.get_digits_from_str(str(phone)):
            return True
        return False

    def __ne__(self, phone):
        return not self == phone

    def is_similar(self, phone):
        phone1 = self.get_digits_from_str(str(self))
        phone2 = self.get_digits_from_str(str(phone))
        if phone1.find(phone2) != -1 or phone2.find(phone1) != -1:
            return True
        return False
    
    def normalize(self, value):
        return self.normalize_phone(value)

if __name__ == "__main__":
    p1 = Phone("777-77-77")
    print(p1, p1.title, p1.order)
    p2 = Phone("(777) 7-777")
    if p1 != p2:
        print("NOT EQ")
    else:
        print("EQ")
    p1.value = "999-99-00"
    print(p1)
    if p1.is_similar("+99(999)19-900"):
        print(f"{str(p1)} is similar")
    else:
        print(f"{str(p1)} is NOT similar")
    # p1 = Phone("Roy Bebru")
