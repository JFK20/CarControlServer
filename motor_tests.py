import requests
import unittest
from getIPAdress import IP_ADDRESS

class TestMotorSpeed(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://" + IP_ADDRESS + ":8000"
        response = requests.get(self.base_url + "/drive/constants")
        response = response.json()
        #print(response)
        self.motorCenter = response["motorCenter"]
        self.motorOffset = response["motorOffset"]

    def test_lower_boundary(self):
        # Test when speed is out of range
        speed = self.motorCenter - (self.motorOffset + 50)
        response = requests.post(f"{self.base_url}/drive/motor/{speed}")
        value = requests.get(f"{self.base_url}/drive/motor/speed")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["speed"], self.motorCenter - self.motorOffset, f"Expected speed 800, but got {value.json()['speed']}")

    def test_in_range_1000(self):
        # Test when speed is in range
        speed = self.motorCenter - (self.motorOffset - 50)
        response = requests.post(f"{self.base_url}/drive/motor/{speed}")
        value = requests.get(f"{self.base_url}/drive/motor/speed")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["speed"], speed, f"Expected speed 1000, but got {value.json()['speed']}")

    def test_in_range_1400(self):
        # Another test when speed is in range
        speed = self.motorCenter + (self.motorOffset - 50)
        response = requests.post(f"{self.base_url}/drive/motor/{speed}")
        value = requests.get(f"{self.base_url}/drive/motor/speed")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")
        self.assertEqual(value.json()["speed"], speed, f"Expected speed 1400, but got {value.json()['speed']}")

    def test_upper_boundary(self):
        # Test when speed is out of range
        speed = self.motorCenter + (self.motorOffset + 50)
        response = requests.post(f"{self.base_url}/drive/motor/{speed}")
        value = requests.get(f"{self.base_url}/drive/motor/speed")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")
        self.assertEqual(value.json()["speed"], self.motorCenter + self.motorOffset, f"Expected speed 1600, but got {value.json()['speed']}")


if __name__ == '__main__':
    unittest.main()
