import unittest
from collections import OrderedDict
from decimal import Decimal

from epicsdbbuilder import ConstArray, Parameter


class TestConstArray(unittest.TestCase):
    par = Parameter("PAR", "Parameter")

    def assert_valid_format_db(self, expected, value):
        arr = ConstArray(value)
        arr.Validate(None, None)
        self.assertEqual(expected, arr.FormatDb(None, None))

    def assert_invalid(self, value, expected_exception=AssertionError):
        with self.assertRaises(expected_exception):
            ConstArray(value).Validate(None, None)

    def test_allow_iterators(self):
        class Iterable:
            def __iter__(self):
                class Iterator:
                    def __init__(self, arr):
                        self.arr = iter(arr)

                    def __next__(self):
                        return next(self.arr)

                    next = __next__  # Python2

                return Iterator([1, 2, 3])

        self.assert_valid_format_db("[1,2,3]", [1, 2, 3])
        self.assert_valid_format_db("[1,2,3]", (1, 2, 3))
        d = OrderedDict([("1", "A"), ("2", "B"), ("3", "C")])
        self.assert_valid_format_db('["1","2","3"]', d)
        self.assert_valid_format_db('["1","2","3"]', "123")
        self.assert_valid_format_db("[1,2,3]", Iterable())

    def test_block_empty_iterators(self):
        self.assert_invalid([])
        self.assert_invalid(())
        self.assert_invalid("")

        class Iterable:
            def __iter__(self):
                class Iterator:
                    def __next__(self):
                        raise StopIteration

                    next = __next__  # Python2

                return Iterator()

        self.assert_invalid(Iterable())

    def test_block_instances_which_are_not_iterators(self):
        self.assert_invalid(None, TypeError)

        self.assert_invalid(True, TypeError)
        self.assert_invalid(1, TypeError)
        self.assert_invalid(2.5, TypeError)
        self.assert_invalid(Decimal("3"), TypeError)

        class MyClass:
            pass

        self.assert_invalid(MyClass(), TypeError)

    def test_allow_boolean_as_elements(self):
        self.assert_valid_format_db("[1]", [True])
        self.assert_valid_format_db("[0]", [False])

    def test_allow_numbers_as_elements(self):
        self.assert_valid_format_db("[1]", [1])
        self.assert_valid_format_db("[2.5]", [2.5])
        self.assert_valid_format_db("[3.5]", [Decimal("3.5")])

    def test_allow_strings_as_elements(self):
        self.assert_valid_format_db('["str"]', ["str"])
        self.assert_valid_format_db('["s1","s2"]', ["s1", "s2"])
        self.assert_valid_format_db('["escaped\\"quotes"]', ['escaped"quotes'])
        self.assert_valid_format_db('[""]', [""])

    def test_allow_parameters_as_elements(self):
        self.assert_valid_format_db('["$(PAR)"]', [self.par])
        self.assert_valid_format_db('["$(PAR)","$(PAR)"]', [self.par, self.par])

    def test_block_none_as_an_element(self):
        self.assert_invalid([None])
        self.assert_invalid(["A", None])
        self.assert_invalid([None, "A"])
        self.assert_invalid(["A", None, "A"])

    def test_allow_mixing_numbers(self):
        self.assert_valid_format_db("[1,1.5,2]", [1, 1.5, Decimal("2")])

    def test_allow_mixing_numbers_and_booleans(self):
        self.assert_valid_format_db("[1,2]", [True, 2])

    def test_allow_mixing_strings_and_parameters(self):
        self.assert_valid_format_db('["str","$(PAR)"]', ["str", self.par])

    def test_block_mixing_numbers_and_strings_or_parameters(self):
        self.assert_invalid([1, "A"])
        self.assert_invalid(["A", 1])
        self.assert_invalid([1, self.par])

    def test_repr(self):
        self.assertEqual("<ConstArray ['ABC']>", repr(ConstArray(["ABC"])))
