from gpio import *
from time import *
from ioeclient import *
from physical import *


DELAY = 50


state = 0

		
def setup():
    IoEClient.setup({
        "type": "Siren",
        "states": [{
            "name": "On",
            "type": "bool",
            "controllable": True
        }]
    })
    add_event_detect(0, lambda : processData(customRead(0)))
    IoEClient.onInputReceive(lambda analogInput : processData(analogInput))
    setState(state)


def processData(data):
    if  len(data) <= 0 :
        return
    setState(int(data))


def setState(newState):
    global state
    state = newState
    if state == True:
        digitalWrite(1, HIGH)
    else:
    	digitalWrite(1, LOW)
    customWrite(0, state)
    IoEClient.reportStates(state)
    setDeviceProperty(getName(), "state", state)


if __name__ == "__main__":
	setup()
	while True:
		delay(DELAY)
