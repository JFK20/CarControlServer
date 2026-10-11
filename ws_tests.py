import json
import time
import requests
import unittest
from websockets.sync.client import connect
from getIPAdress import IP_ADDRESS

class TestWebSocket(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://" + IP_ADDRESS + ":8000"
        self.ws_url = "ws://" + IP_ADDRESS + ":8000/ws/drive"
        #self.base_url = "http://localhost:8000"
        #self.ws_url = "ws://localhost:8000/ws/drive"
        self.ws = self.enterContext(connect(self.ws_url))
        self.initial = json.loads(self.ws.recv())
        constants = self.initial["constants"]
        self.motorCenter = constants["motorCenter"]
        self.motorOffset = constants["motorOffset"]
        self.servoCenter = constants["servoCenter"]
        self.servoOffset = constants["servoOffset"]

    def send(self, message: dict) -> dict:
        self.ws.send(json.dumps(message))
        return json.loads(self.ws.recv())

    def test_initial_state(self):
        self.assertEqual(self.initial["type"], "state")
        for key in ("motor", "servo", "lkas", "constants"):
            self.assertIn(key, self.initial)

    def test_motor_in_range(self):
        speed = self.motorCenter + (self.motorOffset - 50)
        response = self.send({"motor": speed})
        self.assertEqual(response["type"], "state")
        self.assertEqual(response["motor"], speed)
        self.assertNotIn("error", response)

    def test_servo_in_range(self):
        angle = self.servoCenter - (self.servoOffset - 50)
        response = self.send({"servo": angle})
        self.assertEqual(response["servo"], angle)
        self.assertNotIn("error", response)

    def test_motor_out_of_range(self):
        speed = self.motorCenter + (self.motorOffset + 50)
        response = self.send({"motor": speed})
        self.assertEqual(response["motor"], self.motorCenter + self.motorOffset)
        self.assertIn("error", response)

    def test_servo_out_of_range(self):
        angle = self.servoCenter - (self.servoOffset + 50)
        response = self.send({"servo": angle})
        self.assertEqual(response["servo"], self.servoCenter - self.servoOffset)
        self.assertIn("error", response)

    def test_combined(self):
        speed = self.motorCenter + 10
        angle = self.servoCenter - 10
        response = self.send({"motor": speed, "servo": angle})
        self.assertEqual(response["motor"], speed)
        self.assertEqual(response["servo"], angle)

    def test_invalid_json_keeps_connection(self):
        self.ws.send("not json")
        response = json.loads(self.ws.recv())
        self.assertEqual(response["type"], "error")
        response = self.send({"motor": self.motorCenter})
        self.assertEqual(response["motor"], self.motorCenter)

    def test_invalid_type(self):
        response = self.send({"motor": "fast"})
        self.assertEqual(response["type"], "error")

    def test_disconnect_stops_motor(self):
        self.send({"motor": self.motorCenter + 100})
        self.ws.close()
        time.sleep(0.5)
        value = requests.get(f"{self.base_url}/drive/motor/speed")
        self.assertEqual(value.json()["motor"], self.motorCenter)


if __name__ == '__main__':
    unittest.main()
