# pylint: disable-all

import unittest
import requests
import time


class TestApiRoot(unittest.TestCase):
    def test_api_root(self):
        # Poll the service endpoint to ensure
        # that the container has time to start up
        url = "http://localhost:8080"
        timeout = 15  # seconds
        start_time = time.time()
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass

            if time.time() - start_time > timeout:
                self.fail("Service did not become ready within the timeout period")

            time.sleep(0.5)  # Wait before retrying

        # Call API and assign to a variable
        result = response.json()

        self.assertEqual(result["greeting"], "Hello from AISMR")
