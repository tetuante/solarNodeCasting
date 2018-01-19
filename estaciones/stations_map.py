#!/usr/bin/env python2

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Loading our data, probably we won't need everything but whatever:
stations = pd.read_csv('stations.txt',sep='\t')
station_id = stations['Station'].astype(basestring)
lat = stations['Latitude']
long = stations['Longitude']
sensor = stations['Sensor']
CF = stations['CF']

#Let's plot:
fig, ax = plt.subplots(facecolor='w')

#We need a loop over here to annotate the name of every station in the scatter plot:
for key, row in stations.iterrows():
    ax.scatter(row['Longitude'], row['Latitude'])
    ax.annotate(row['Station'],xy=(row['Longitude'], row['Latitude']))

plt.title('Oahu Solar Measurement Grid Stations')
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

#Let's set a small value to fit the data in the X&Y axes without fitting it too much (20 is an arbitrary value)
x_ax_fit = abs(long.max() - long.min()) / 20
y_ax_fit = abs(lat.max() - lat.min()) / 20

plt.xlim((long.min() - x_ax_fit), (long.max() + x_ax_fit))
plt.ylim((lat.min() - y_ax_fit), (lat.max() + y_ax_fit))

plt.show()
