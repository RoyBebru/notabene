"""Class AddressBook

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


from collections import UserDict
import os
import re

from notabene.record import Record


class AddressBookException(Exception):
    def __init__(self, *args, **kwargs):
        # Call parent constructor
        super(Exception, self).__init__(*args, **kwargs)


class AddressBook(UserDict):
    # Common pattern for one name: first last middle
    pattern_name = (r"\b\w(?![0-9_])"
                       r"(?:(?<![0-9_])(?:\w|['-])(?![0-9_]))*"
                       r"(:?\w(?![0-9_]))?\b")
    # Name consists of 1..3 words each can contain "'" or "-" in the middle
    pattern_name = re.compile(pattern_name
                        + r"(?:\s" + pattern_name
                        + r"(?:\s" + pattern_name + r")?"
                        + r")?", re.IGNORECASE) # up to 3 word name pattern

    def __init__(self, records=()):
        """ Instead tuple() in records can be used list[] or vice versa:
        ab = AddressBook(
            ("Mykola", (("Phone", "111-22-33"), ("Phone", "111-44-55"), ...)))
        )
        ab = AddressBook((
            ("Mykola": (("Phone", "111-22-33"), ("Phone", "111-44-55"), ...))),
            ("Oleksa": (("Phone", "333-22-33"), ("Phone", "333-44-55"), ...))),
        ))
        """
        super().__init__({})
        self[None] = records # call __setitem__()
        self.is_modified = False

    @staticmethod
    def is_similar(name1: str, name2: str) -> bool:
        """Smart names comparation.
        Names must be normalized
        """
        words1 = name1.lower().split(' ')
        words2 = name2.lower().split(' ')
        for w1 in range(len(words1)):
            for w2 in range(len(words2)):
                if words2[w2] is None:
                    continue
                if words1[w1] == words2[w2]:
                    words1[w1] = None
                    words2[w2] = None
                    break
                elif words1[w1].find(words2[w2]) != -1:
                    words2[w2] = None
                    continue
                elif words2[w2].find(words1[w1]) != -1:
                    words1[w1] = None
                    break
        if len(tuple(x for x in filter(
                    lambda x: x is not None, words1))) == 0 or \
                len(tuple(x for x in filter(
                    lambda x: x is not None, words2))) == 0:
            return True
        return False

    @staticmethod
    def equal_by_combination(name1: str, name2: str) -> bool:
        """Case insensitive equal by words combination
            Names must be normalized.
        """
        if len(name1) != len(name2):
            return False
        words1 = name1.lower().split(' ')
        words2 = name2.lower().split(' ')
        for word1 in words1:
            for word2 in words2:
                if word1 == word2:
                    break
            else:
                # No break was made: one word is not equal
                return False
        return True

    @staticmethod
    def normalize_name(name: str) -> str:
        # Removing start/end spaces and change many spaces with one
        name = " ".join(str(name).split())
        return name

    @staticmethod
    def verify_name(name: str):
        """Check name format"""
        m = AddressBook.pattern_name.search(name)
        if not bool(m):
            raise AddressBookException(f"incorrect name '{name}'")
        if m.start() != 0:
            raise AddressBookException(f"extra symbol(s) '{name[:m.start()]}' in the start")
        if m.end() != len(name):
            raise AddressBookException(f"extra symbol(s) '{name[m.start():]}' in the end")
        # Name is proven
        return

    def __getitem__(self, key):
        """
         key    | Return
        --------+-------------------------------------
        1) None | ( ("Name1", ("Phone", "111222333"), ...),
                |   ("Name2", ("Phone", "111222333"), ...), ...
                | )
        2) str  | Record
        """
        if key is None:
            return tuple((name, record.as_tuple_of_tuples())
                         for (name, record) in self.data.items())
        elif isinstance(key, str):
            return self.data.get(key) # if absent return None
        raise AddressBookException(f"unsopported key {key}")

    def __setitem__(self, key, value):
        """
         key    | value              | Action
        --------+--------------------+-------------------------------------
        1) None | ("Name", ("Phone", "111222333"), ...)
                |                    | self.data[value "Name"]
                |                    |     = Record(value w/o "Name")
        2) None | ( ("Name", ("Phone", "111222333"), ...),
                |   ("Name", ("Phone", "111222333"), ...), ...
                | )                  | many times (1)
        3) str  | (("Phone", "111222333"), ...)
                |                    | self.data[key] = Record(value)
        4) str  | Record             | self.data[key] = Record
        5) str  | str                | change name "key" with "value"
        """
        if key is None:
            if len(value) == 0:
                self.data.clear()
                self.is_modified = True
                return
            if isinstance(value, tuple) or isinstance(value, list):
                if isinstance(value[0], str):
                    self.data[value[0]] = Record(value[1:])         # (1)
                    self.is_modified = True
                    return
                for item in value:                                  # (2)
                    if not isinstance(item[0], str):
                        raise AddressBookException(
                            f"absent required name as "
                            f"the first item in {item}")
                    self.data[item[0]] = Record(item[1:])
                    self.is_modified = True
                return
            raise AddressBookException(f"not supported value {value}")
        elif isinstance(key, str):
            key = self.normalize_name(key)
            self.verify_name(key)
            if isinstance(value, tuple) or isinstance(value, list): # (3)
                self.data[key] = Record(value)
            elif isinstance(value, Record):                         # (4)
                self.data[key] = value
            elif isinstance(value, str):
                # Change name (rename)                              # (5)
                self.rename(key, value)
            else:
                raise AddressBookException(f"not supported value {value}")
        else:
            raise AddressBookException(f"not supported key {key}")

        self.is_modified = True
        return

    def rename(self, key: str, name: str) -> str:
        name = self.normalize_name(name)
        if key == name:
            return key # nothing to do
        if not self.equal_by_combination(key, name) \
                and self.is_any_equal_by_combination(name):
            raise AddressBookException(f"name {name} already exist")
        self.data[name] = self.data[key]
        self.data.pop(key, None) # without exception
        return name

    def get_similar(self, name:str) -> tuple:
        """For each key in self.keys() that is similar to name
           return (Name1, Name2, ...)
        """
        name = self.normalize_name(name)
        return tuple(key for key in self.data.keys() if self.is_similar(key, name))

    def is_any_equal_by_combination(self, name: str) -> bool:
        name = self.normalize_name(name)
        for key in self.data.keys():
            if self.equal_by_combination(key, name):
                return True
        return False

    def __str__(self):
        return str(self[None])

    def report(self, names = None, index=1) -> str:
        if names is None:
            names = list(self.data.keys())
        elif isinstance(names, str):
            names = (names,)
        if isinstance(names, tuple) or isinstance(names, list):
            index -= 1
            indent = len(str(len(names) + index))
            name_format = f"#%-{indent}d Name: %s"
            indent += len("# ")
            return (os.linesep * 2).join(
                name_format % (index := index + 1, name)
                + self.data[name].report(indent)
                for name in names)
        return ""

    def _sample_to_regex(self, sample):
        """Converts:
        Matches any zero or more characters: '*' -> '.*'
        Matches any one character: '?' -> '.?'
        Matches exactly one character that is a member of
            the string string: '[string]' -> '[string]'
        Removes the special meaning of the character
            that follows it: '\' -> '\'
        """
        sample = re.sub(r"(?<!\\)\*", r".*", sample)
        sample = re.sub(r"(?<!\\)\?", r".?", sample)
        sample = re.sub(r"(?<!\\)\+", r"\+", sample)
        sample = re.sub(r"(?<!\\)\(", r"\(", sample)
        sample = re.sub(r"(?<!\\)\)", r"\)", sample)
        sample = re.sub(r"(?<!\\)\|", r"\|", sample)
        return sample

    def iter_by_sample(self, sample: str, names=None):
        if names is None:
            names = list(self.data.keys())
        elif isinstance(names, str):
            names = (names,)
        if isinstance(names, tuple) or isinstance(names, list):
            try:
                rex = re.compile(self._sample_to_regex(sample),
                                re.IGNORECASE|re.MULTILINE)
            except re.error:
                raise AddressBookException("error sample in metasymbols")
            index = 1
            for name in names:
                if rex.search(self.report((name,), index=index)):
                    yield name
                index += 1

    def JSON_helper(self):
        ab = {}
        for (name, record) in self.data.items():
            rec_list = list(record.as_tuple_of_tuples())
            rec_list.sort(reverse=True, key=lambda it: it[0])
            ab[name] = rec_list
        return ab
