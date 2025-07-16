# pylint: disable-all

import unittest
import requests


class TestApi(unittest.TestCase):
    def test_api_root(self):
        url = "http://localhost:8500"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result["greeting"], "Hello from AISMR")
