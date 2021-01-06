import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))

import unittest
from epicsdbbuilder.recordbase import quote_string

class TestQuoteString(unittest.TestCase):
    def test_empty(self):
        self.assertEqual('""', quote_string(''))

    def test_string_without_escaping(self):
        self.assertEqual('"ABC:123.FIELD"', quote_string('ABC:123.FIELD'))

    def test_string_with_escaping(self):
        self.assertEqual('"A\\"C"', quote_string('A"C'))


if __name__ == '__main__':
    unittest.main()
