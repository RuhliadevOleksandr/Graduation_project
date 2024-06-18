from time import *
import math
from physical import *
from gpio import *
from environment import Environment
from ioeclient import IoEClient


DELAY = 1000
VARIANCE = 2.5
SUNLIGHT_MULTIPLIER = 0.3

rate = 0.
state = 0
brightness = 0.
minBrightness = 33.3


def setup ():
    IoEClient.setup({
        "type": "Led",
        "states": [{
            "name": "On",
            "type": "bool",
            "controllable": True
        }, {
            "name": "Light Brightness",
            "type": "number",
            "decimalDigits": 1
        }, {
            "name": "Min Light Brightness",
            "type": "number",
            "decimalDigits": 1,
            "controllable": True,
            "minValue": 10,
            "maxValue": 100
        }]
    })
    IoEClient.onInputReceive(lambda input : processData(input))
    add_event_detect(0, lambda : processData(customRead(0)))
    setState(state)


def processData(data):
    global minBrightness
    if  len(data) <= 0 :
        return
    data = data.split(",")
    setState(int(data[0]))
    minBrightness = float(data[2])


def setState(newState):
    global state
    state = newState
    sendReport()
    
    
def sendReport():
    report = str(state) + ',' + str(brightness) + ',' + str(minBrightness)
    customWrite(0, report)
    IoEClient.reportStates(report)
    setDeviceProperty(getName(), "state", state)
    setDeviceProperty(getName(), "level", brightness)
    setDeviceProperty(getName(), "min level", minBrightness)


def mouseEvent(pressed, x, y, firstPress):
    if firstPress:
        if state == 0:
            setState(1)
        else:
            setState(0)


def loop():
    global rate, brightness
    if state == 0:
        brightness = 0
        rate = 0
    else:
        brightness = minBrightness - Environment.get("Sunlight") * SUNLIGHT_MULTIPLIER
        rate -= Environment.get("Visible Light") - VARIANCE - minBrightness
        if rate < 0:
            brightness = 0
            rate = 0
    Environment.setContribution("Visible Light", rate, rate, False)
    setComponentOpacity("black", 1 - brightness / minBrightness)
    sendReport()


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
