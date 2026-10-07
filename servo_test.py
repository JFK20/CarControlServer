import requests
import unittest
from getIPAdress import IP_ADDRESS

class TestServoAngle(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://" + IP_ADDRESS + ":8000"
        response = requests.get(self.base_url + "/drive/constants")
        response = response.json()
        self.servoCenter = response["servoCenter"]
        self.servoOffset = response["servoOffset"]

    def test_lower_boundary(self):
        # Test when angle is out of range
        angle = self.servoCenter - (self.servoOffset + 50)
        response = requests.post(f"{self.base_url}/drive/servo/{angle}")
        value = requests.get(f"{self.base_url}/drive/servo/angle")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["servo"], self.servoCenter - self.servoOffset)

    def test_in_range_1000(self):
        # Test when angle is in range
        angle = self.servoCenter - (self.servoOffset - 50)
        response = requests.post(f"{self.base_url}/drive/servo/{angle}")
        value = requests.get(f"{self.base_url}/drive/servo/angle")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["servo"], angle)

    def test_in_range_1400(self):
        # Another test when angle is in range
        angle = self.servoCenter + (self.servoOffset - 50)
        response = requests.post(f"{self.base_url}/drive/servo/{angle}")
        value = requests.get(f"{self.base_url}/drive/servo/angle")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["servo"], angle)

    def test_upper_boundary(self):
        # Test when angle is out of range
        angle = self.servoCenter + (self.servoOffset + 50)
        response = requests.post(f"{self.base_url}/drive/servo/{angle}")
        value = requests.get(f"{self.base_url}/drive/servo/angle")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["servo"], self.servoCenter + self.servoOffset)


if __name__ == '__main__':
    unittest.main()
