from options import Options
from time import *
from physical import *
from gpio import *
from environment import Environment
from ioeclient import IoEClient


DELAY = 200
X_DETECT_DISTANCE = 1335
Y_DETECT_DISTANCE = 1335
MIN_FLAME_WAVELENGTH = 760
MAX_FLAME_WAVELENGTH = 1100
MINUTES_IN_HOUR = 60
SECONDS_IN_MINUTE = 60


detected = False


def setup ():       
    IoEClient.setup({
        'type': 'Fire Sensor',
        'states': [{
            'name': 'Fire Detected',
            'type': 'bool',
            'controllable': False
        }]
    })


def loop ():
    global detected
    value = LOW 
    x = getCenterX() - X_DETECT_DISTANCE / 2
    y = getCenterY() - Y_DETECT_DISTANCE / 2
    devices = devicesAt(x, y, X_DETECT_DISTANCE,  Y_DETECT_DISTANCE)
    deviceProperties = []
    for device in devices:
        deviceProperty = getDeviceProperty(device, 'IR')
        if deviceProperty:
            deviceProperties.append(deviceProperty)
    for property in deviceProperties:
        propertyValue = int(property)
        if (MIN_FLAME_WAVELENGTH <= propertyValue) and (MAX_FLAME_WAVELENGTH > propertyValue):
            value = HIGH
    digitalWrite(0, value)
    if value > 0 and not detected:
        seconds = Environment.getTimeInSeconds()
        hours = seconds / (SECONDS_IN_MINUTE * MINUTES_IN_HOUR)
        seconds %= SECONDS_IN_MINUTE * MINUTES_IN_HOUR
        minutes = seconds / SECONDS_IN_MINUTE
        seconds %= SECONDS_IN_MINUTE
        print '{"fireDectedTime": "' + "%02d:%02d:%02d" % (hours, minutes, seconds) + '"}'
        detected = True
    elif value  == 0:
        detected = False
    IoEClient.reportStates(value)
    setDeviceProperty(getName(), "state", value)


if __name__ == "__main__":
    setup()
    while True:
        loop()
        delay(DELAY)
