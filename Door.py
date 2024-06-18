from time import *
from physical import *
from gpio import *
from environment import Environment
from ioeclient import IoEClient


GASES = ["Argon", "CO", "CO2", "Hydrogen", "Helium", "Methane", "Nitrogen", "O2", "Ozone", "Propane", "Smoke"]
GAS_MAX_IMPACT = -0.02
TEMPERATURE_TRANSFERENCE_MULTIPLIER = 1.25
HUMIDITY_TRANSFERENCE_MULTIPLIER = 1.25
GASES_TRANSFERENCE_MULTIPLIER = 2
VOLUME_AT_RATE = 100000
SECONDS_IN_HOUR = 3600
X_READ_DISTANCE = 50
Y_READ_DISTANCE = 50
DELAY = 350


doorState = 0
lockState = 1
startTime = 0
cardID = 0
lastCardID = 0


def setup ():
    IoEClient.setup({
        "type": "Door",
        "states": [{
                "name": "Card ID",
                "type": "number"
            },
            {
                "name": "Lock",
                "type": "options",
                "options": {
                    "0": "Unlock",
                    "1": "Lock"
                },
                "controllable": True
        }]
    })
    IoEClient.onInputReceive(lambda input: processData(input))
    setDoorState(doorState)
    setLockState(lockState)
    add_event_detect(0, lambda : setLockState(digitalRead(0)))


def processData(data):
    if len(data) <= 0:
        return
    data = data.split(",")
    setLockState(int(data[1]))


def setDoorState (state):
    global doorState
    doorState = state
    if  state == 0:
        digitalWrite(1, LOW)
        setComponentOpacity("led", 1)
    else:
        digitalWrite(1, HIGH)
        setComponentOpacity("led", 0)
    sendReport()


def setLockState (state):
    global lockState
    lockState = state
    if state == 0:
        digitalWrite(2, LOW)
    else:
        digitalWrite(2, HIGH)
    sendReport()


def sendReport():
    setDeviceProperty(getName(), "door state", doorState)
    setDeviceProperty(getName(), "lock state", lockState)
    IoEClient.reportStates(str(cardID) + "," + str(lockState))


def mouseEvent (pressed, x, y, firstPress):
    global startTime
    if firstPress:
        if  isPointInRectangle(x, y, 10,40,5,10) :
            if  lockState == 0:
                setLockState(1)
        else:
            if doorState == 0 and lockState == 0:
                setDoorState(1)
                startTime = time()
                updateEnvironment()


def isPointInRectangle (x,y, rx, ry, width, height):
    if width <= 0 or height <= 0:
        return False
    return (x >= rx and x <= rx + width and y >= ry and y <= ry + height)


def loop():
    global cardID, lastCardID
    if doorState == 1 and time() - startTime > 4:
        setDoorState(0)
        updateEnvironment()
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


def updateEnvironment ():
    if  doorState == 1:
        for gas in GASES:
            max = Environment.get(gas) * GAS_MAX_IMPACT
            rate = float(max) / SECONDS_IN_HOUR * VOLUME_AT_RATE / Environment.getVolume()
            Environment.setContribution(gas, rate, max, True)
            Environment.setTransferenceMultiplier(gas, GASES_TRANSFERENCE_MULTIPLIER)
        Environment.setTransferenceMultiplier("Ambient Temperature", TEMPERATURE_TRANSFERENCE_MULTIPLIER)
        Environment.setTransferenceMultiplier("Humidity", HUMIDITY_TRANSFERENCE_MULTIPLIER)
    else:
        for gas in GASES:
            Environment.setContribution(gas, 0, 0, True)
            Environment.removeCumulativeContribution(gas)
            Environment.setTransferenceMultiplier(gas, 1)
        Environment.setTransferenceMultiplier("Ambient Temperature", 1)
        Environment.setTransferenceMultiplier("Humidity", 1)


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
