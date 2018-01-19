import wifi
from machine import RTC
from utime import sleep, time, mktime
from os import listdir
import ujson

# RTC modified class (It's meant to be used with UTC time)
class modRTC(RTC):

    # Check if needed files already exist and create them if they are missing
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
            sleepParams = '23:59:59 60000' # Avoid errors if file is empty or missing
        sleepParams = sleepParams.split(' ')
        sleepParams = tuple(int(i) for i in sleepParams[0].split(':')) + (int(sleepParams[1]),)
        return sleepParams

    # Get sleep parameters (sunset time + night length) from sunrise-sunset.org servers
    def syncSleepParams(self):
        todaySunset = ujson.loads(wifi.https_get('https://api.sunrise-sunset.org/json?lat=40.45&lng=-3.72&date=today&formatted=0').split('\n')[-1])['results']['sunset']
        tomorrowSunrise = ujson.loads(wifi.https_get('https://api.sunrise-sunset.org/json?lat=40.45&lng=-3.72&date=tomorrow&formatted=0').split('\n')[-1])['results']['sunrise']

        sleepTime = todaySunset.split('T')[-1].split('+')[0]

        sleepStart = mktime(tuple(int(i) for i in todaySunset.split('T')[0].split('-')) + tuple(int(i) for i in todaySunset.split('T')[-1].split('+')[0].split(':')) + (0, 0))
        sleepEnd = mktime(tuple(int(i) for i in tomorrowSunrise.split('T')[0].split('-')) + tuple(int(i) for i in tomorrowSunrise.split('T')[-1].split('+')[0].split(':')) + (0, 0))

        sleepLength = (sleepEnd - sleepStart) * 1000 # ms
        sleepParams = sleepTime + ' ' + str(sleepLength)

        self.storeLastSyncedSleepParams(sleepParams)
