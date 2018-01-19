from machine import RTC
import lora
from utime import sleep, time
from os import listdir

# RTC modified class (It's meant to be used with UTC time)
class modRTC(RTC):

    # Check if needed files already exist and create them if they are missing
    # lastRTCSync file is used to store the last time the RTC was synced
    # sleepParams file is used to store the sleep parameters of the next night (sunset time + night length)
    def __init__(self):
        ld = listdir('/flash/')
        if 'lastRTCSync' in ld:
            print('lastRTCSync file already exists')
        else:
            print('Could not find lastRTCSync file, attempting to create it...')
            with open('/flash/lastRTCSync', 'w') as f:
                print('lastRTCSync file has been created')
                f.close()

        if 'sleepParams' in ld:
            print('sleepParams file already exists')
        else:
            print('Could not find sleepParams file, attempting to create it...')
            with open('/flash/sleepParams', 'w') as f:
                print('sleepParams file has been created')
                f.close()

    # Returns datetime as string ('aaaa-mm-dd hh:mm:ss UTC')
    def getDatetime(self):
        datetime = self.now()
        return '{:4d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} UTC'.format(datetime[0], datetime[1], datetime[2], datetime[3], datetime[4], datetime[5])

    # Returns date as string ('aaaa-mm-dd')
    def getDate(self):
        datetime = self.now()
        return '{:4d}-{:02d}-{:02d}'.format(datetime[0], datetime[1], datetime[2])

    # Returns time as string ('hh:mm:ss')
    def getTime(self):
        datetime = self.now()
        return '{:02d}:{:02d}:{:02d}'.format(datetime[3], datetime[4], datetime[5])

    # Store last synced datetime in a file
    def storeLastSyncedDatetime(self):
        with open('/flash/lastRTCSync', 'w') as f:
            f.write(self.getDatetime())
            f.close()

    # Read last synced datetime from file
    def readLastSyncedDatetime(self):
        datetime = ''
        with open('/flash/lastRTCSync', 'r') as f:
            datetime = f.read()
            f.close()
        return datetime

    # Store last synced sleep parameters in a file
    def storeLastSyncedSleepParams(self, sleepParams):
        with open('/flash/sleepParams', 'w') as f:
            f.write(sleepParams)
            f.close()

    # Read last synced sleep parameters from file and return a tuple (hh, mm, ss, night_length)
    def readLastSyncedSleepParams(self):
        sleepParams = ''
        with open('/flash/sleepParams', 'r') as f:
            sleepParams = f.read()
            f.close()
        if( sleepParams == '' ):
            sleepParams = '23:59:59 60000' # Avoid future errors if file is empty
        sleepParams = sleepParams.split(' ')
        sleepParams = tuple(int(i) for i in sleepParams[0].split(':')) + (int(sleepParams[1]),)
        return sleepParams

    # Sync RTC with LoRa gateway and get today's sleep parameters
    def loraSync(self):
        date_time = b''
        while date_time == b'':
            # Send request
            print('Requesting time...')
            tStart = time() # Record request time in order to compensate delays
            date_time = lora.sendReceive('getTime') # Send getTime request and attempt to receive the data from gateway
            sleep(3)
            lora.sendReceive('0') # Clear unread messages in case of failure when receiving data

        # Get time parameters from received data
        year = int(date_time[:4])
        month = int(date_time[5:7])
        day = int(date_time[8:10])

        hour = int(date_time[11:13])
        minute = int(date_time[14:16])
        second = int(date_time[17:19])
        microsecond = int(date_time[20:26])

        # Set RTC time with received data, any delay caused by the previous process is taken into account
        self.init((year, month, day, hour, minute, second + (time() - tStart), microsecond, 0))
        self.storeLastSyncedDatetime() # Store last synced datetime in the filesystem

        sleep(3)

        # Get sleep parameters (sunset and night length)
        sleepParams = b''
        while sleepParams == b'':
            # Send request
            print('Requesting sleep parameters...')
            sleepParams = lora.sendReceive('getSleepParams') # Send request and receive data from gateway
            sleep(3)
            lora.sendReceive('0') # Clear unread messages in case of fail when receiving data

        # Decode bytearray using UTF-8 code
        sleepParams = sleepParams.decode('UTF-8')
        self.storeLastSyncedSleepParams(sleepParams) # Store sleep parameters in filesystem
