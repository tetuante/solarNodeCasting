#!/usr/bin/env python3

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import math

#Loading our data, probably we won't need everything but whatever:
stations = pd.read_csv('stations.txt',sep='\t')
station_id = str(stations['Station'])
lat = stations['Latitude']
lon = stations['Longitude']
sensor = stations['Sensor']
CF = stations['CF']


#We should transform the latitudes and longitudes into meters to make the visualization easier:
lon_min = math.radians(lon.min())
lon_max = math.radians(lon.max())
lat_min = math.radians(lat.min())
lat_max = math.radians(lat.max())

nticks = 10

lat_rad = []
lon_rad = []
for i in range(len(lat)):
    lat_rad.append(math.radians(lat[i]))
    lon_rad.append(math.radians(lon[i]))
#into meters using the min values as our "zero"
lat_meters = []
lon_meters = []
for i in range(len(lat)):
    lat_meters.append(lat_rad[i] - lat_min)
    lon_meters.append(lon_rad[i] - lon_min)


#Let's plot:
fig, ax = plt.subplots(facecolor='w')

#We need a loop over here to annotate the name of every station in the scatter plot:
for key, row in stations.iterrows():
    ax.scatter(row['Longitude'], row['Latitude'])
    ax.annotate(row['Station'],xy=(row['Longitude'], row['Latitude']))

plt.title('Oahu Solar Measurement Grid Stations.\nDistance in meters.')
#ax.set_xlabel("West                                                      East")
#ax.set_ylabel("South                                                     North")

#Let's set a small value to fit the data in the X&Y axes without fitting it too much (20 is an arbitrary value)

x_ax_fit = abs(lon.max() - lon.min()) / 20
y_ax_fit = abs(lat.max() - lat.min()) / 20

plt.xlim((lon.min() - x_ax_fit), (lon.max() + x_ax_fit))
plt.ylim((lat.min() - y_ax_fit), (lat.max() + y_ax_fit))


latitudes = np.linspace(lat.min(),lat.max(),nticks)
longitudes = np.linspace(lon.min(),lon.max(),nticks)
R = 6371000
xdists=[]
ydists=[]
#Equirectangular aproximation: https://www.movable-type.co.uk/scripts/latlong.html
#x and y refer to that approximation in this loop:
for i in range(nticks):
	x = math.radians(longitudes[i]-longitudes[0]) * math.cos((math.radians(latitudes[0]+latitudes[0]))/2)
	d = int(R * abs(x))
	xdists.append(d)
for i in range(nticks):
	y = math.radians(latitudes[i]-latitudes[0])
	d = int(R * abs(y))
	ydists.append(d)



plt.xticks(longitudes,xdists)
plt.yticks(latitudes,ydists)
plt.grid(which='both',linewidth=0.3)
plt.savefig('stations_map.png',dpi=500,bbox_inches = 'tight')
