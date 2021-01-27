import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import unittest
from decimal import Decimal
from epicsdbbuilder import ConstArray, Parameter, ResetRecords


class TestConstArray(unittest.TestCase):
    par = Parameter('PAR', 'Parameter')

    def assertValidFormatDb(self, expected, value):
        arr = ConstArray(value)
        arr.Validate(None, None)
        self.assertEqual(expected, arr.FormatDb(None, None))

    def assertInvalid(self, value):
        self.assertRaises(AssertionError, \
            lambda: ConstArray(value).Validate(None, None))

    def test_allow_iterators(self):
        class Iterable:
            def __iter__(self):
                class Iterator:
                    def __init__(self, arr):
                        self.arr = iter(arr)

                    def __next__(self):
                        return next(self.arr)
                return Iterator([1, 2, 3])

        self.assertValidFormatDb('[1,2,3]', [1, 2, 3])
        self.assertValidFormatDb('[1,2,3]', (1, 2, 3))
        self.assertValidFormatDb('["1","2","3"]', {'1': 'A', '2': 'B', '3': 'C'})
        self.assertValidFormatDb('["1","2","3"]', '123')
        self.assertValidFormatDb('[1,2,3]', Iterable())

    def test_block_empty_iterators(self):
        self.assertInvalid([])
        self.assertInvalid(())
        self.assertInvalid('')

        class Iterable:
            def __iter__(self):
                class Iterator:
                    def __next__(self):
                        raise StopIteration
                return Iterator()

        self.assertInvalid(Iterable())

    def test_block_instances_which_are_not_iterators(self):
        self.assertInvalid(None)

        self.assertInvalid(True)
        self.assertInvalid(1)
        self.assertInvalid(2.5)
        self.assertInvalid(Decimal('3'))

        class MyClass:
            pass
        self.assertInvalid(MyClass())

    def test_allow_boolean_as_elements(self):
        self.assertValidFormatDb('[1]', [True])
        self.assertValidFormatDb('[0]', [False])

    def test_allow_numbers_as_elements(self):
        self.assertValidFormatDb('[1]', [1])
        self.assertValidFormatDb('[2.5]', [2.5])
        self.assertValidFormatDb('[3.5]', [Decimal('3.5')])

    def test_allow_strings_as_elements(self):
        self.assertValidFormatDb('["str"]', ['str'])
        self.assertValidFormatDb('["s1","s2"]', ['s1', 's2'])
        self.assertValidFormatDb('["escaped\\"quotes"]', \
            ['escaped"quotes'])
        self.assertValidFormatDb('[""]', [''])

    def test_allow_parameters_as_elements(self):
        self.assertValidFormatDb('["$(PAR)"]', [self.par])
        self.assertValidFormatDb('["$(PAR)","$(PAR)"]', \
            [self.par, self.par])

    def test_block_none_as_an_element(self):
        self.assertInvalid([None])
        self.assertInvalid(['A', None])
        self.assertInvalid([None, 'A'])
        self.assertInvalid(['A', None, 'A'])

    def test_allow_mixing_numbers(self):
        self.assertValidFormatDb('[1,1.5,2]', \
            [1, 1.5, Decimal('2')])

    def test_allow_mixing_numbers_and_booleans(self):
        self.assertValidFormatDb('[1,2]', \
            [True, 2])

    def test_allow_mixing_strings_and_parameters(self):
        self.assertValidFormatDb('["str","$(PAR)"]', \
            ['str', self.par])

    def test_block_mixing_numbers_and_strings_or_parameters(self):
        self.assertInvalid([1, 'A'])
        self.assertInvalid(['A', 1])
        self.assertInvalid([1, self.par])

    def test_repr(self):
        self.assertEqual('<ConstArray [\'ABC\']>', \
            repr(ConstArray(['ABC'])))


if __name__ == '__main__':
    unittest.main()
