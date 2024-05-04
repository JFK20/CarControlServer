import requests
import unittest


class TestServoAngle(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://127.0.0.1:8000/drive/constants"
        response = requests.post(self.base_url)
        response = response.json()
        #print(response)
        self.servoCenter = response["servoCenter"]
        self.servoOffset = response["servoOffset"]

    def test_lower_boundary(self):
        # Test when angle is out of range
        angle = self.servoCenter - (self.servoOffset + 50)
        response = requests.post(f"http://127.0.0.1:8000/drive/servo/{angle}")
        value = requests.get("http://127.0.0.1:8000/drive/servo/angle")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["angle"], self.servoCenter - self.servoOffset, f"Expected angle 800, but got {value.json()['angle']}")

    def test_in_range_1000(self):
        # Test when angle is in range
        angle = self.servoCenter - (self.servoOffset - 50)
        response = requests.post(f"http://127.0.0.1:8000/drive/servo/{angle}")
        value = requests.get("http://127.0.0.1:8000/drive/servo/angle")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["angle"], 1100, f"Expected angle 1000, but got {value.json()['angle']}")

    def test_in_range_1400(self):
        # Another test when angle is in range
        angle = self.servoCenter + (self.servoOffset - 50)
        response = requests.post(f"http://127.0.0.1:8000/drive/servo/{angle}")
        value = requests.get("http://127.0.0.1:8000/drive/servo/angle")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["angle"], 2000, f"Expected angle 1400, but got {value.json()['angle']}")

    def test_upper_boundary(self):
        # Test when angle is out of range
        angle = self.servoCenter + (self.servoOffset + 50)
        response = requests.post(f"http://127.0.0.1:8000/drive/servo/{angle}")
        value = requests.get("http://127.0.0.1:8000/drive/servo/angle")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["angle"], self.servoCenter + self.servoOffset, f"Expected angle 1600, but got {value.json()['angle']}")


if __name__ == '__main__':
    unittest.main()
