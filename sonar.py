import pigpio

# echo pulses longer than this are out of range (> ~4 m)
MAX_PULSE_US = 25000


class Sonar:
    # HC-SR04 ultrasonic sensor, the echo pulse is timed by pigpiod in microseconds
    def __init__(self, pi: pigpio.pi, trigger_pin: int, echo_pin: int):
        self.pi = pi
        self.trigger_pin = trigger_pin
        self.distance = None
        self._rise = None

        pi.set_mode(trigger_pin, pigpio.OUTPUT)
        pi.write(trigger_pin, 0)
        pi.set_mode(echo_pin, pigpio.INPUT)
        self._cb = pi.callback(echo_pin, pigpio.EITHER_EDGE, self._edge)

    def _edge(self, gpio, level, tick):
        if level == 1:
            self._rise = tick
        elif level == 0 and self._rise is not None:
            pulse = pigpio.tickDiff(self._rise, tick)
            # sound travels there and back: 58 us per cm
            self.distance = pulse / 58.0 if pulse < MAX_PULSE_US else None
            self._rise = None

    def trigger(self):
        # reset first so a missing echo doesn't repeat the last value
        self.distance = None
        self.pi.gpio_trigger(self.trigger_pin, 10, 1)

    def cancel(self):
        self._cb.cancel()
