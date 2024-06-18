from time import *
from physical import *
from gpio import *


DELAY = 350
MIN = 5
MAX = 10
MAX_SENSOR_LEVEL = 20.
MAX_10BIT_VALUE = 1023
level = 0.
state = 0


def setup ():
    setSprinklerState(state)


def setSprinklerState (newState):
    global state
    state = newState
    if state == 0:
        digitalWrite(1, LOW)
    else:
        digitalWrite(1, HIGH)


def loop ():
    waterLevel = analogRead(A0)* MAX_SENSOR_LEVEL / MAX_10BIT_VALUE 
    setLevel(waterLevel)
    if level < MIN:
        setSprinklerState(1)
    elif level > MAX:
        setSprinklerState(0)


def setLevel (newLevel):
    global level
    level = newLevel
    customWrite(0, str("%.2f"%(level)))


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
