from time import *
from physical import *
from gpio import *
from ioeclient import IoEClient


X_READ_DISTANCE = 50
Y_READ_DISTANCE = 50
DELAY = 350


turnstileState = 1
tripodeState = 0
startTime = 0
cardID = 0
lastCardID = 0


def setup ():
	IoEClient.setup({
		"type": "Turnstile",
		"states": [{
			"name": "On",
			"type": "bool",
			"controllable": True
		}, {
            "name": "Card ID",
            "type": "number"
        }, {
			"name": "Lock",
			"type": "options",
			"options": {
                0: "Lock",
                1: "Unlock"
			},
			"controllable": True
		}]
	})
	IoEClient.onInputReceive(lambda input : processData(input)) 
	add_event_detect(0, lambda : processData(customRead(0)))
	setTurnstileState(turnstileState)
	setTripodeState(tripodeState)


def mouseEvent (pressed, x, y, firstPress):
    if firstPress:
        if  turnstileState == 1 and tripodeState == 1 :
            setTripodeState(0)

def processData (data):
    if  len(data) < 1 :
        return
    global startTime
    data = data.split(",")
    turnstileStateData = int(data[0])
    tripodeStateData = int(data[2])
    if  turnstileStateData == 0 :
        setTurnstileState(0)
    elif  turnstileStateData == 1 :
        setTurnstileState(1)
        setTripodeState(0)
    if  tripodeStateData == 0 :
        setTripodeState(0)
    elif  tripodeStateData == 1 :
        setTripodeState(1)
        startTime = time()


def sendReport ():
    report = str(turnstileState) + "," + str(cardID) + "," + str(tripodeState)
    customWrite(0, report)
    IoEClient.reportStates(report)
    setDeviceProperty(getName(), "turnstile state", turnstileState)
    setDeviceProperty(getName(), "tripode state", tripodeState)


def setTurnstileState (state):
    global turnstileState
    if  state == 0:
        digitalWrite(1, LOW)
        setComponentOpacity("led", 0)
    else:
        digitalWrite(1, HIGH)
        setComponentOpacity("led", 1)
    turnstileState = state
    sendReport()


def setTripodeState (state):
    global tripodeState
    if  state == 0 :
        digitalWrite(2, LOW)
    else:
        digitalWrite(2, HIGH)
    tripodeState = state
    sendReport()


def loop():
    global cardID, lastCardID
    if tripodeState == 1 and time() - startTime > 4:
        setTripodeState(0)
    found = False
    devices = devicesAt(getCenterX(), getCenterY(), X_READ_DISTANCE, Y_READ_DISTANCE)
    lockName = getName()
    for device in devices:
        if device == lockName:
            continue
        cardID = getDeviceProperty(device, 'CardID')
        found = True
        break
    if found:
        if lastCardID != cardID:
            lastCardID = cardID
            sendReport()
    else:
        lastCardID = cardID = 0
    sendReport()


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
