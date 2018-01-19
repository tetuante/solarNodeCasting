import pycom
import time
from machine import Pin
from dht import DHT

powerPin = Pin('G28', mode=Pin.OUT)
powerPin(0)

pycom.heartbeat(False)
pycom.rgbled(0x000008) # blue
powerPin(1)
time.sleep(2)
th0 = DHT('G24',1)
th1 = DHT('G11',1)
result0 = th0.read()
result1 = th1.read()
# powerPin(0)

if result0.is_valid():
    pycom.rgbled(0x001000) # green
    print('Temperature0: {:3.1f}'.format(result0.temperature/1.0))
    print('Humidity0: {:3.1f}'.format(result0.humidity/1.0))
if result1.is_valid():
    pycom.rgbled(0x001000) # green
    print('Temperature1: {:3.1f}'.format(result1.temperature/1.0))
    print('Humidity1: {:3.1f}'.format(result1.humidity/1.0))
