#!/usr/bin/env python3

import json
import numpy as np
import pandas as pd
import matplotlib
#Some computers have a problem with pyplot and TKinter. This workaround solves it.
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

ax.set_xlabel("West                                                      East")
ax.set_ylabel("South                                                     North")

#Let's set a small value to fit the data in the X&Y axes without fitting it too much (20 is an arbitrary value)

x_ax_fit = abs(lon.max() - lon.min()) / 20
y_ax_fit = abs(lat.max() - lat.min()) / 20

plt.xlim((lon.min() - x_ax_fit), (lon.max() + x_ax_fit))
plt.ylim((lat.min() - y_ax_fit), (lat.max() + y_ax_fit))

#Calculate distance in meters from the most southwestern point to the most northeastern in the east and north direction and the middle point
lat_mid = (lat.min() + lat.max()) / 2
lat_mid_rad = math.radians(lat_mid)
lon_mid = (lon.min() + lon.max()) / 2
lon_mid_rad = math.radians(lon_mid)
xtick_locs = [lon.min(),lon_mid,lon.max()]
ytick_locs = [lat.min(),lat_mid,lat.max()]
R = 6371000
x_dist_0 = int(R * math.sqrt((math.cos((lat_min + lat_min)/2) * (lon_mid_rad - lon_min)) **2))
x_dist_1 = int(R * math.sqrt((math.cos((lat_min + lat_min)/2) * (lon_max - lon_min)) **2))
xtick_lbls = [0,x_dist_0,x_dist_1]
y_dist_0 = int(R * (lat_mid_rad - lat_min))
y_dist_1 = int(R * (lat_max - lat_min))
ytick_lbls = [0,y_dist_0,y_dist_1]


plt.xticks(xtick_locs,xtick_lbls)
plt.yticks(ytick_locs,ytick_lbls)

plt.savefig('stations_map2.png',bbox_inches = 'tight')
