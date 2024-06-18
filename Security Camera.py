from gpio import *
from time import *
from ioeclient import *
from physical import *
from environment import *
import math


DELAY = 500

state = 0
imageLoop = 0


def setup():
    global state
    IoEClient.setup({
        "type": "Security Camera",
        "states": [{
            "name": "On",
            "type": "bool",
            "controllable": True
        },
        {
            "name": "Image",
            "type": "image"
        }]
    })
    IoEClient.onInputReceive(processData)
    add_event_detect(0, lambda : setState(digitalRead(0)))
    sendReport()


def mouseEvent(pressed, x, y, firstPress):
    global state
    if firstPress:
        if state == True:
        	setState(0)
        else:
        	setState(1)


def processData(data):
    if  len(data) <= 0 :
        return
    data = data.split(",")
    setState(int(data[0]))


def sendReport():
    global state
    global imageLoop
    report = str(state) + ","
    if state is 0:
        report += '../art/IoE/SmartDevices/camera_off.png'
    else:
        report += '../art/IoE/SmartDevices/camera_image'+ str(imageLoop)+'.png'
        imageLoop = imageLoop + 1
        if  imageLoop >= 3:
            imageLoop = 0
    IoEClient.reportStates(report)
    if state > 0:
        print '{"imagePath": "' + report.split(",")[1] + '"}'
    setDeviceProperty(getName(), "state", state)


def setState(newState):
    global state
    if  newState is 0 :
        digitalWrite(1, LOW)
    else:
        digitalWrite(1, HIGH)
    state = newState


if __name__ == "__main__":
    setup()
    while True:
        sendReport()
        delay(DELAY)
