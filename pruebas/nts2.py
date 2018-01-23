#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import json
import pysolar

with open('config.json', 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

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

# Create output directory if it doesn't exist
if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

# Copy config.json to output directory
with open('config.json', 'r') as cfg_file:
    with open(dest_folder + 'config.json', 'w') as f:
        f.write(cfg_file.read())

# Find out what is the first possible prediction
first_prediction_index = 0
for station in cfg_data['params']:
    index = params[station]['nsamples'] + params[station]['offset']
    if index > first_prediction_index:
        first_prediction_index = index
first_prediction = first_prediction_index * time_granularity

with open(orig_folder + target_station + '/' + target_station + '.csv', 'r') as f:
    y = pd.read_csv(f)[first_prediction::time_granularity]

last_prediction = y.last_valid_index()
# print('$$$$$' + target_station + '$$$$$')
# print('FIRST PREDICTION: {}\nLAST PREDICTION: {}\nROWS: {}\n'.format(y.first_valid_index(), y.last_valid_index(), len(y)))

for station in cfg_data['params']:
    nsamples = params[station]['nsamples']
    offset = params[station]['offset']
    with open(orig_folder + station + '/' + station + '.csv', 'r') as f:
        df = pd.read_csv(f)

    # print('#####' + station + '#####')

    for ns in range(nsamples):
        dist = (ns + offset + 1) * time_granularity
        first_sample = first_prediction - dist
        last_sample = last_prediction - dist
        _x = df[first_sample:last_sample + time_granularity:time_granularity]
        # print('FIRST SAMPLE: {}\nLAST SAMPLE: {}\nROWS: {}\n'.format(_x.first_valid_index(), _x.last_valid_index(), len(_x)))
        col_name = station + '_ns' + str(ns)
        _x = _x.rename(columns={station: col_name})
        x = pd.concat([x,_x[col_name].reset_index(drop=True)], axis=1)

y = y.reset_index(drop=True)
col_name = target_station + '_target'
y = y.rename(columns={target_station: col_name})
matrix = pd.concat([x,y[col_name].reset_index(drop=True)], axis=1)

print(matrix)

#WARNING: this will overwrite any existing CSV file with the same path and name
with open(dest_folder + dest_file, 'w') as f:
    matrix.to_csv(f,header=True,index=False)
