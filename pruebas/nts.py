#!/usr/bin/env python3

import os
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

orig_time_columns_names = cfg_data['orig_time_columns_names']

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

y = pd.read_csv(orig_folder + target_station + '/' + target_station + '.csv')

print('$$$$$$$$$$ ' + target_station + ' $$$$$$$$$$')
print('TOTAL ROWS: {}\n'.format(len(y)))

# We will skip intermediate samples for now
y = y[first_prediction::time_granularity]
last_prediction = y.last_valid_index()

print('FIRST PREDICTION: {}\nLAST PREDICTION: {}\nROWS: {}\n'.format(y.first_valid_index(), y.last_valid_index(), len(y)))

for station in cfg_data['params']:
    nsamples = params[station]['nsamples']
    offset = params[station]['offset']
    df = pd.read_csv(orig_folder + station + '/' + station + '.csv')

    print('########## ' + station + ' ##########')
    print('TOTAL ROWS: {}\n'.format(len(df)))

    for ns in range(nsamples):
        dist = (ns + offset + 1) * time_granularity
        first_sample = first_prediction - dist
        last_sample = last_prediction - dist
        # We will skip intermediate samples for now
        _x = df[first_sample:last_sample + time_granularity:time_granularity]
        print('FIRST SAMPLE: {}\nLAST SAMPLE: {}\nROWS: {}\n'.format(_x.first_valid_index(), _x.last_valid_index(), len(_x)))
        # Rename GHI column to include station name and nsample
        ghi_col = station + '_ns' + str(ns)
        _x = _x.rename(columns={station: ghi_col})
        # Only GHI is needed. We need to reset the index in order to concatenate columns properly
        x = pd.concat([x,_x[ghi_col].reset_index(drop=True)], axis=1)

# Rename GHI column to include station name and target indicator
ghi_col = target_station + '_target'
y = y.rename(columns={target_station: ghi_col})

# Only GHI is needed. We need to reset the index in order to concatenate columns properly
matrix = pd.concat([x,y[ghi_col].reset_index(drop=True)], axis=1)

#WARNING: this will overwrite any existing CSV file with the same path and name
matrix.to_csv(dest_folder + dest_file, header=True, index=False)
