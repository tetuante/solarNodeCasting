# DHT Pure Python library for Pycom board using new function pulses_get

This simple class can be used for reading temperature and humidity values from DHT11 and DTH22 sensors on Pycom Board. Thanks to szazo for the original source code. 

# Usage

1. Instantiate the `DHT` class with the pin number and type of sensor (0=DTH11, 1=DTH22) as constructor parameters.
2. Call `read()` method, which will return `DHTResult` object with actual values and error code. 

For example:

```python
import pycom
import time
from machine import Pin
from dth import DTH

pycom.heartbeat(False)
pycom.rgbled(0x000008) # blue
th = DTH('P3',0)
time.sleep(2)
result = th.read()
if result.is_valid():
    pycom.rgbled(0x001000) # green
    print("Temperature: %d C" % result.temperature)
    print("Humidity: %d %%" % result.humidity)

For working example, see `dht11_example.py` (you probably need to adjust pin for your configuration)


# License

This project is licensed under the terms of the MIT license.
