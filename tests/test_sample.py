# pylint: disable-all

import unittest

class TestSample(unittest.TestCase):
    def test_sample(self):
        # We are simply checking whether 42==42!
        self.assertEqual(42, 42)