#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import json
import pysolar

with open('config.json', 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

input_stations = cfg_data['input_stations']
target_station = cfg_data['target_station']

orig_folder = cfg_data['orig_folder']
dest_folder = cfg_data['dest_folder']
dest_file = cfg_data['dest_file']

time_granularity = cfg_data['time_granularity']

params = cfg_data['params']

orig_columns_names = cfg_data['orig_columns_names']

aggregation = cfg_data["aggregation"]

x = pd.DataFrame() # This matrix will include the features
y = pd.DataFrame() # This matrix will include the target
latitude = params[target_station]['latitude']
longitude = params[target_station]['longitude']
# Find out what is the oldest sample (biggest nsamples + offset)
oldest_sample = 0
for station in input_stations:
    index = params[station]['nsamples'] + params[station]['offset']
    if index > oldest_sample:
        oldest_sample = index

oldest_sample *= time_granularity

with open(orig_folder + target_station + '/' + target_station + '.csv', 'r') as f:
    y = pd.read_csv(f, dtype=str)['ghi'][oldest_sample+time_granularity::time_granularity]

print(len(y))
