"""Class Field

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""

from abc import ABC, abstractmethod


class Field(ABC):
    def __init__(self, value="", title="", order=0, is_unique=False):
        # Field title, such as "Phone", "E-mail", "Birthday", etc
        self.title = title
        # Field to sort
        self.order = order
        self._value = ""
        self.value = value
        self.is_unique = is_unique

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = self.normalize(value)

    @abstractmethod
    def normalize(self, value):
        raise NotImplementedError("absent method implementaion")

    def __str__(self):
        return self.value

    def __eq__(self, value):
        return self.value.lower() == str(value).lower()

    def __ne__(self, value):
        return not self == value

    def report(self):
        return self.value


if __name__ == "__main__":
    f1 = Field("data", "Comment", 90)
    f1.value = "Datum"
    f1.order = 85
    print(f1, f1.title, f1.order)
