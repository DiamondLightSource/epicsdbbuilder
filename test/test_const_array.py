import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import unittest
from decimal import Decimal
from epicsdbbuilder import ConstArray, Parameter, ResetRecords


class TestConstArray(unittest.TestCase):
    par = Parameter('PAR', 'Parameter')

    def test_list_allows_only_numbers_strings_parameters(self):
        ConstArray([True])
        ConstArray([1])
        ConstArray([2.5])
        ConstArray([Decimal('3.5')])
        ConstArray(['str'])
        ConstArray([self.par])
        self.assertRaises(AssertionError, lambda: ConstArray([None]))

    def test_list_cannot_mix_string_numbers(self):
        self.assertRaises(AssertionError, lambda: ConstArray([1, 'A']))
        self.assertRaises(AssertionError, lambda: ConstArray(['A', 1]))
        self.assertRaises(AssertionError, lambda: ConstArray([1, self.par]))

    def test_only_lists_tuples_allowed(self):
        ConstArray([1, 2, 3])
        ConstArray((1, 2, 3))
        self.assertRaises(AssertionError, lambda: ConstArray(None))
        self.assertRaises(AssertionError, lambda: ConstArray('a'))
        self.assertRaises(AssertionError, lambda: ConstArray({ 'a': 1 }))

    def test_FormatDb_single_string(self):
        self.assertEqual('["ABC"]', \
            ConstArray(['ABC']).FormatDb(None, None))

    def test_FormatDb_single_string_with_escaping(self):
        self.assertEqual('["A\\"C"]', \
            ConstArray(['A"C']).FormatDb(None, None))

    def test_FormatDb_single_parameter(self):
        self.assertEqual('["$(PAR)"]', \
            ConstArray([self.par]).FormatDb(None, None))

    def test_FormatDb_multiple_strings(self):
        self.assertEqual('["A","B","C"]', \
            ConstArray(['A', 'B', 'C']).FormatDb(None, None))

    def test_FormatDb_multiple_numbers(self):
        self.assertEqual('[1,2,3]', \
            ConstArray([1, 2, 3]).FormatDb(None, None))

    def test_FormatDb_multiple_booleans(self):
        self.assertEqual('[0,1]', \
            ConstArray([False, True]).FormatDb(None, None))

    def test_FormatDb_empty(self):
        self.assertEqual('[""]', \
            ConstArray([]).FormatDb(None, None))
        self.assertEqual('[""]', \
            ConstArray(()).FormatDb(None, None))

    def test_Validate_strings_and_parameter_only(self):
        ConstArray(["A", self.par, "C"]).Validate(None, None)

    def test_Validate_numbers_only(self):
        ConstArray([False, 1, 2.5, Decimal('3.5')]).Validate(None, None)

    def test_repr(self):
        self.assertEqual('<ConstArray [\'ABC\']>', \
            repr(ConstArray(['ABC'])))


if __name__ == '__main__':
    unittest.main()
