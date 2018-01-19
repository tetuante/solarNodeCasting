'''
This script converts the datetime of the input CSV files to sun position coordinates
and creates new CSV files to store these data.
'''

import csv
from sunposition import sunpos
from datetime import datetime
from sys import argv
from glob import glob
import os

lat = 40.451
lon = -3.726
ele = 657

normalize = True

print('Cleaning workspace...')
for name in os.listdir():
    if 'after_' in name:
        print('Deleting ' + name + '...')
        os.remove(name)

if(argv[1] == 'clean'):
    exit()

filelist = []
for arg in argv[1:]:
    filelist += glob(arg)

for name in filelist:

    print('Processing ' + name + '...')

    inputCSV = open(name, newline='')
    reader = csv.reader(inputCSV)
    next(reader) # Skip the first row (header)

    data = {}
    maxAzimuth = 0.0
    maxElevation = 0.0
    maxTemperature = 0.0
    maxHumidity = 0.0
    maxvPanel = 0.0
    maxvPyra = 0.0

    for row in reader:
        date_time = row[0].split(' UTC')[0]
        date = date_time.split(' ')[0]
        time = date_time.split(' ')[1]

        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])

        hour = int(time.split(':')[0])
        minute = int(time.split(':')[1])
        second = int(time.split(':')[2])

        dt = datetime(year, month, day, hour, minute, second, 0)

        azimuth, zenith = sunpos(dt,lat,lon,ele)[:2]
        elevation = 90 - zenith

        azimuth = round(azimuth, 3)
        elevation = round(elevation, 3)
        temperature = float(row[2])
        humidity = float(row[3])
        vPanel = float(row[4])
        vPyra = float(row[5])

        date = date.replace('-','')

        if date not in data.keys():
            data[date] = ()

        if 7 < hour < 15:
            data[date] += ([azimuth, elevation, temperature, humidity, vPanel, vPyra],)

    if normalize:
        for date in data.keys():
            maxAzimuth = 0
            maxElevation = 0
            maxTemperature = 0
            maxHumidity = 0
            maxvPanel = 0
            maxvPyra = 0
            for row in data[date]:
                maxAzimuth = row[0] if row[0] > maxAzimuth else maxAzimuth
                maxElevation = row[1] if row[1] > maxElevation else maxElevation
                maxTemperature = row[2] if row[2] > maxTemperature else maxTemperature
                maxHumidity = row[3] if row[3] > maxHumidity else maxHumidity
                maxvPanel = row[4] if row[4] > maxvPanel else maxvPanel
                maxvPyra = row[5] if row[5] > maxvPyra else maxvPyra
            for row in data[date]:
                row[0] = row[0] / maxAzimuth
                row[1] = row[1] / maxElevation
                row[2] = row[2] / maxTemperature
                row[3] = row[3] / maxHumidity
                row[4] = row[4] / maxvPanel
                row[5] = row[5] / maxvPyra

    for date in data.keys():
        outputCSV = open('after_' + date + '.csv', 'w', newline='')
        writer = csv.writer(outputCSV)
        writer.writerow(['azimuth', 'elevation', 'temperature', 'humidity', 'vPanel', 'vPyra']) # Insert the header
        writer.writerows(data[date])
        outputCSV.close()

    inputCSV.close()
    print('Done')
