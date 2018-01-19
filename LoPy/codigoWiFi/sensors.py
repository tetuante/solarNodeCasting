from machine import ADC, I2C, Pin
from utime import sleep_ms, sleep_us
from math import sqrt

# ADC class
class ADCCLASS:
    def __init__(self, readPin, N):
        self.N = N # Number of readings per measure
        self.adc = ADC() # Call the constructor
        self.readPin = self.adc.channel(pin=readPin, attn = ADC.ATTN_11DB) # Assign the analog pin
        # Allocate memory for some relevant variables
        self.value = 0 # ADC counts
        self.stdDev = 0 # Standard deviation of N readings
        self.voltage = 0 # Voltage
        self.deltaV = 0 # Voltage's Standard deviation

    def measure(self, vBias):
        # Compute value as the mean of N readings
        measureSum = 0
        measureSum2 = 0
        for i in range(self.N):
            measure = self.readPin()
            measureSum += measure # Accumulate readings
            measureSum2 += measure * measure
            sleep_us(200) # Wait 200 us before reading the next value (ESP32's ADC has a sampling rate of 6 KHz)

        self.value = measureSum / self.N # Compute the mean
        self.stdDev = sqrt((measureSum2 / self.N) - (self.value * self.value) )

        # Compute voltage according to the ADC's transfer curve and bias voltage
        self.voltage = ADCCLASS.__countsToVolts(self.value) - vBias # [V]
        self.deltaV = self.stdDev * self.voltage / self.value # [V]

        # Print results
        # print('Value: {:4.3f}'.format(self.value, self.stdDev))
        # print('Voltage: {:1.3f} +- {:1.3f}'.format(self.voltage, self.deltaV))

    # Function that computes a voltage from ADC counts
    def __countsToVolts(counts):
        return ( ( counts + 161.660 ) / 1248.094 ) # [V]


# HIH sensor class
class HIH:

    i2c = I2C(0, I2C.MASTER, baudrate=200000) # Create i2c object and set the baudrate

    def __init__(self):
        # Allocate memory for some relevant variables
        self.rawData = bytearray(4)
        self.status = 0
        self.rawTemperature = bytearray(2)
        self.rawHumidity = bytearray(2)
        self.temperature = 0
        self.humidity = 0

    def measure(self):
        try:
            sleep_ms(75)
            HIH.i2c.writeto(0x27, '0') # Measure Request
            sleep_ms(45)
            HIH.i2c.readfrom_into(0x27, self.rawData) # Fetch data

            # Response (4 bytes): | S1 S0 B13-B8 | B7-B0 | T13-T6 | T5-T0 X X |
            # S1 S0
            # 0 0 normal operation | 0 1 stale data | 1 0 command mode | 1 1 unused
            self.status = self.rawData[0] >> 6
            # T13-T0
            self.rawTemperature = ((self.rawData[2] << 8) | self.rawData[3]) >> 2
            # B13-B0
            self.rawHumidity = ((self.rawData[0] << 8) | self.rawData[1]) & 0x3FFF

            # Temperature in Celsius (-40-125 ºC)
            self.temperature = (self.rawTemperature * 165 / 16382) - 40
            # Relative Humidity percentage (0-100 %)
            self.humidity = self.rawHumidity * 100 / 16382
        except:
            print('HIH sensor not found')
