# pylint: disable-all

import unittest
import requests


class TestApp(unittest.TestCase):
    def test_app_root(self):
        url = "http://localhost:8501"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
