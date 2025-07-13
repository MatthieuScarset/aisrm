# pylint: disable-all

import unittest
import requests
import time


class TestApiRoot(unittest.TestCase):
    def test_api_root(self):
        # Adding a 15s sleep timer to ensure
        # that the container has time to start up
        time.sleep(15)

        # Call API and assign to a variable
        url = "http://localhost:8080"
        result = requests.get(url).json()

        self.assertEqual(result["greeting"], "Hello from AISMR")
