# Das ist der Fake-Sensor. Wenn hier etwas schiefgeht, 
# betrifft es nur die Live-Daten, nicht das UI.

import math


class FakeBreathSource:
    def __init__(self):
        self.t = 0.0

    def get_value(self) -> float:
        self.t += 0.1
        return math.sin(self.t)
