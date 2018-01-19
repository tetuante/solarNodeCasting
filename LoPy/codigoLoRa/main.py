import sensors, lora, modrtc
from machine import deepsleep, Pin, DAC, SD
from utime import sleep_ms, time
from os import mount, unmount

samplingInterval = 60 # s

# Booleans used to enable/disable LoRa communication, deepsleep and data logging
enableLoRa = True
enableSleep = True
logData = True

# Record start time
if enableSleep:
    tStart = time()

# RTC instantiation
rtc = modrtc.modRTC()

# Shutdown pin for OpAmps
powerPin = Pin('G28', mode=Pin.OUT)
powerPin(0) # Turn them off

# Generate bias voltages using DAC
vBiasPanel = DAC('G9')
vBiasPanel.write(0.135) # approximately 0.5 V
vBiasBatt = DAC('G8')
vBiasBatt.write(0.525) # approximately 1.7 V

# Instantiate objects
hih = sensors.HIH() # Temperature and humidity sensor
vPanel = sensors.ADCCLASS('G5', 5000) # Transimpedance amplifier output voltage
vBatt = sensors.ADCCLASS('G4', 5000) # Battery voltage (differential amplifier, unity gain)
vPyra = sensors.ADCCLASS('G0', 5000) # Pyranometer output voltage (non-inverting summing amplifier, unity gain)
vBiasP = sensors.ADCCLASS('G31', 5000) # Bias voltage for vPanel and vPyra
vBiasB = sensors.ADCCLASS('G30', 5000) # Bias voltage for vBatt

# Connect to LoRa network and sync RTC if needed
if enableLoRa:
    print('Connecting to LoRa network...')
    lora.connect()
    # Sync RTC once a day
    if rtc.getDate() != rtc.readLastSyncedDatetime().split(' ')[0]:
        print('Syncing RTC...')
        rtc.loraSync()
    else:
        print('RTC has already been synced today!')

print('Measuring...')
# Turn OpAmps on
powerPin(1)
# Ensure that OpAmps are on before measuring
sleep_ms(1)
# Measure voltages, temperature and humidity
hih.measure()
vBiasP.measure(0.0)
vBiasB.measure(0.0)
vPanel.measure(vBiasP.voltage)
vPyra.measure(vBiasP.voltage)
vBatt.measure(-vBiasB.voltage)
# Turn OpAmps off
powerPin(0)

# Save measurement's timestamp
timestamp = rtc.getDatetime()

# Compose the message
msg = '{:2.1f},{:3.1f},{:2.3f},{:2.3f},{:2.3f},{:2.3f},{:2.3f}'.format(hih.temperature, hih.humidity, vPanel.voltage, vPyra.voltage, vBatt.voltage, vBiasP.voltage, vBiasB.voltage)

# Send the message to the LoRa gateway
if enableLoRa:
    print('Sending data...')
    lora.send(msg)

# Log data to a file stored in SD card
if logData:
    try:
        print('Saving data to SD card...')
        # SD instantiation
        sd = SD()
        mount(sd, '/sd')
        # Filename pattern: aaaammdd.csv
        with open('/sd/' + timestamp.split(' ')[0].replace('-', '') + '.csv', 'a') as datafile:
            datafile.write( timestamp + ',' + msg + '\n' )
            datafile.close()
        unmount('/sd')
    except:
        print('Error while saving data')

# Enter deep-sleep mode to save power
if enableSleep:
    print(rtc.getDatetime())
    sleepParams = rtc.readLastSyncedSleepParams()
    if( rtc.now()[3:6] >= sleepParams[:3] ):
        print('Good night!')
        deepsleep(sleepParams[3])
    # Record time elapsed from start time
    t = time() - tStart
    # Sleep until completing 60 seconds from start time
    if t < samplingInterval:
        print('Sleeping...')
        deepsleep((samplingInterval - t)*1000)
    else:
        print('We are late! No time to sleep...')
        deepsleep(1) # Reset if elapsed time is greater than 60 seconds
