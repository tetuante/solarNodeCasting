import time
from machine import Pin
from onewire import DS18X20
from onewire import OneWire

powerPin = Pin('G28', mode=Pin.OUT)
powerPin(1)

ow = OneWire(Pin('G11'))
temp = DS18X20(ow) # DS18X20 must be powered on on instantiation (rom scan)

powerPin(0)

def medir(n=1):
    powerPin(1)
    for i in range(n):
        temp.start_convertion()
        time.sleep_ms(750)
        print('{:3.4f}'.format(temp.read_temp_async()))
    powerPin(0)
