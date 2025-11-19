# Add package directory to path for debugging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import unittest 
from enumex import *
from enum import auto
import pickle

class EnumExA(EnumEx):
    V1 = auto()
    V2 = auto()
class EnumExB(EnumExA):
    V3 = auto()
    V4 = auto()

class IntEnumExA(IntEnumEx):
    V1 = auto()
    V2 = auto()
class IntEnumExB(IntEnumExA):
    V3 = auto()
    V4 = auto()

class FlagExA(FlagEx):
    V1 = auto()
    V2 = auto()
class FlagExB(FlagExA):
    V3 = auto()
    V4 = auto()

class IntFlagExA(IntFlagEx):
    V1 = auto()
    V2 = auto()
class IntFlagExB(IntFlagExA):
    V3 = auto()
    V4 = auto()

class StrEnumExA(StrEnumEx):
    V1 = auto()
    V2 = auto()
class StrEnumExB(StrEnumExA):
    V3 = auto()
    V4 = auto()

class EnumExPickleTests(unittest.TestCase):

    def test_pickle_enumex_member(self):
        _test_pickle_member(self, EnumExA.V1)
        _test_pickle_member(self, EnumExB.V1)

    def test_pickle_intenumex_member(self):
        _test_pickle_member(self, IntEnumExA.V1)
        _test_pickle_member(self, IntEnumExB.V1)

    def test_pickle_flagex_member(self):
        _test_pickle_member(self, FlagExA.V1)
        _test_pickle_member(self, FlagExB.V1)

    def test_pickle_IntFlagex_member(self):
        _test_pickle_member(self, IntFlagExA.V1)
        _test_pickle_member(self, IntFlagExB.V1)

    def test_pickle_StrEnumex_member(self):
        _test_pickle_member(self, StrEnumExA.V1)
        _test_pickle_member(self, StrEnumExB.V1)

    def test_pickle_enumex_types(self):
        def test_pickle_type(enum_type:type[EnumEx]):
            self.assertTrue(issubclass(enum_type, EnumEx), msg=f"Type to pickle is EnumEx subclass")

            data = pickle.dumps(enum_type)
            obj = pickle.loads(data)
            self.assertIs(obj, enum_type, msg=f"Pickle type is {enum_type}")
            self.assertListEqual(list(obj), list(enum_type), msg=f"Pickle type members equal")

        test_pickle_type(EnumExA)
        test_pickle_type(EnumExB)
        test_pickle_type(IntEnumExA)
        test_pickle_type(IntEnumExB)
        test_pickle_type(FlagExA)
        test_pickle_type(FlagExB)
        test_pickle_type(IntFlagExA)
        test_pickle_type(IntFlagExB)
        test_pickle_type(StrEnumExA)
        test_pickle_type(StrEnumExB)


def _test_pickle_member(case:unittest.TestCase, enum_member:EnumEx, msg:str = None):
    data = pickle.dumps(enum_member)
    obj = pickle.loads(data)

    case.assertIsInstance(enum_member, EnumEx, msg=f"Member to pickle is EnumEx instance")
    case.assertIsInstance(obj, type(enum_member), msg=f"Pickle member is {type(enum_member)}")
    case.assertIs(obj, enum_member, msg=f"Pickle member is {enum_member}")


if __name__ == "__main__":
    unittest.main()