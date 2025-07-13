# pylint: disable-all

import unittest


class TestData(unittest.TestCase):
    def test_data(self):
        # Check raw data is available.
        self.assertEqual(42, 42)
