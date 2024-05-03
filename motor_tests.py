import requests
import unittest


class TestMotorSpeed(unittest.TestCase):

    def test_lower_boundary(self):
        # Test when speed is out of range
        response = requests.post("http://127.0.0.1:8000/motor/700")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")

    def test_in_range_1000(self):
        # Test when speed is in range
        response = requests.post("http://127.0.0.1:8000/motor/1000")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")

    def test_in_range_1400(self):
        # Another test when speed is in range
        response = requests.post("http://127.0.0.1:8000/motor/1400")
        self.assertEqual(response.status_code, 200, f"Expected status code 200, but got {response.status_code}")

    def test_upper_boundary(self):
        # Test when speed is out of range
        response = requests.post("http://127.0.0.1:8000/motor/1700")
        self.assertEqual(response.status_code, 400, f"Expected status code 400, but got {response.status_code}")


if __name__ == '__main__':
    unittest.main()
