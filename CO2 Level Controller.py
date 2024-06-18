from time import *
from physical import *
from gpio import *


DELAY = 1000
MIN = 0.05
MAX = 0.06
MAX_SENSOR_LEVEL = 0.2
MAX_10BIT_VALUE = 1023
level = 0.
state = 0


def setup ():
    setWindowState(state)


def setWindowState (newState):
    global state
    state = newState
    if state == 0:
        digitalWrite(1, LOW)
    else:
        digitalWrite(1, HIGH)


def loop ():
    CO2Level = analogRead(A0)* MAX_SENSOR_LEVEL / MAX_10BIT_VALUE
    setLevel(CO2Level)
    if level < MIN:
        setWindowState(0)
    elif level > MAX:
        setWindowState(1)


def setLevel (newLevel):
    global level
    level = newLevel
    customWrite(0, str("%.3f"%(level)) + "%")


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
