from machine import ADC
from math import sqrt
from utime import sleep_us

adc = ADC()

'''
Connects the internal 1.1v to external GPIO. It can only be connected to P22, P21 or P6.
It is recommended to only use P6 on the WiPy, on other modules this pin is connected to the radio.
'''
# adc.vref_to_pin('P22')

'''
If called without any arguments, this function returns the current calibrated voltage (in millivolts) of the 1.1v reference.
Otherwise it will update the calibrated value (in millivolts) of the internal 1.1v reference.

Use the ADC.vref_to_pin(*,pin) method and a voltmeter to find out the actual Vref.
'''
adc.vref(1059)

apin = adc.channel(pin='G5', attn = ADC.ATTN_11DB)

'''
This function measures the ADC pin N times with a sampling period of delay.

mean voltage, rms voltage and standard deviation are computed.
'''
def measure(N=1000, delay=200):

    asum = 0
    sqsum = 0

    meanVolt = 0
    sqmeanVolt = 0
    rmsVolt = 0
    stdDev = 0

    for i in range(N):
        volt = apin.voltage()

        asum += volt
        sqsum += volt*volt

        sleep_us(delay)

    meanVolt = asum / N
    sqmeanVolt = sqsum / N
    rmsVolt = sqrt(sqmeanVolt)
    stdDev = sqrt(sqmeanVolt - (meanVolt*meanVolt))

    print('meanVoltage:\t{:10.0f} mV'.format(meanVolt))
    print('rmsVoltage:\t{:10.0f} mV'.format(rmsVolt))
    print('stdDev:\t\t{:10.0f} mV'.format(stdDev))
