import time
from machine import Pin, ADC, DAC
from onewire import DS18X20
from onewire import OneWire
from dht import DHT

adc = ADC()
# adc.vref_to_pin('P21')
adc.vref(1058)

vBiasDAC = DAC('P22')
vBiasDAC.write(0.135) # approximately 0.5 V

vPanel = adc.channel(pin='P13', attn = ADC.ATTN_11DB)
vBatt = adc.channel(pin='P14', attn = ADC.ATTN_11DB)
vPyra = adc.channel(pin='P15', attn = ADC.ATTN_11DB)
vTherm = adc.channel(pin='P17', attn = ADC.ATTN_11DB)
vBias = adc.channel(pin='P18', attn = ADC.ATTN_11DB)

powerPin = Pin('P8', mode=Pin.OUT)
powerPin(1)

ow = OneWire(Pin('P4'))
temp = DS18X20(ow) # DS18X20 must be powered on on instantiation (rom scan)

powerPin(0)

th = DHT('P3',1)

def medir(n=1):
    powerPin(1)
    time.sleep_ms(1000)
    for i in range(n):
        result = th.read()
        temp.start_convertion()
        time.sleep_ms(750)
        print('Temperature DS18B20: {:3.4f}'.format(temp.read_temp_async()))
        print('Temperature DHT22: {:3.1f}'.format(result.temperature/1.0))
        print('Humidity DHT22: {:3.1f}'.format(result.humidity/1.0))
        print('vPanel: {:3.4f}'.format(vPanel.voltage()))
        print('vBatt: {:3.4f}'.format(vBatt.voltage()))
        print('vPyra: {:3.4f}'.format(vPyra.voltage()))
        print('vTherm: {:3.4f}'.format(vTherm.voltage()))
        print('vBias: {:3.4f}'.format(vBias.voltage()))
    powerPin(0)
