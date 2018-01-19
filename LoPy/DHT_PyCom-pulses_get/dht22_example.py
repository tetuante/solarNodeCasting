import pycom
import time
from machine import Pin
from dth import DTH

pycom.heartbeat(False)
pycom.rgbled(0x000008) # blue
th = DTH('P3',1)
time.sleep(2)
result = th.read()
if result.is_valid():
    pycom.rgbled(0x001000) # green
    print('Temperature: {:3.2f}'.format(result.temperature/1.0))
    print('Humidity: {:3.2f}'.format(result.humidity/1.0))
