#!/usr/bin/env python3

import os
import pandas as pd
import json
import optparse
import sys

def addOptions(parser):
   parser.add_option("--configFile", default="",
             help="Config json file for the data to pass to the model")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.configFile:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

#with open('config.json', 'r') as cfg_file:
with open(options.configFile, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

target_station = cfg_data['target_station']

orig_folder = cfg_data['orig_folder']
dest_folder = cfg_data['dest_folder']
dest_file_suffix = cfg_data['dest_file_suffix']

time_granularity = cfg_data['time_granularity']

params = cfg_data['params']
stations = [station for station in params if params[station]['nsamples'] > 0]
nstations = len(stations)

aggregation = cfg_data["aggregation"]
relative = cfg_data["relative"]
decimal_pos = cfg_data["decimal_pos"]

if relative:
    rad_col = '_rel'
else:
    rad_col = '_ghi'

# Create output directory if it doesn't exist
if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

# Copy config.json to output directory
#with open('config.json', 'r') as cfg_file:
with open(options.configFile, 'r') as cfg_file:
    with open(dest_folder + options.configFile, 'w') as f:
        f.write(cfg_file.read())

# Get dates that are available for all stations
dates = set([date[:8] for date in os.listdir(orig_folder + stations[0])])
for station in stations:
    station_dates = set([date[:8] for date in os.listdir(orig_folder + station)])
    dates.intersection_update(station_dates)

dates = list(dates)
ndates = len(dates)

print('Days available: {}'.format(ndates))

# Find out what is the first possible prediction
first_prediction_index = 0
for station in cfg_data['params']:
    index = params[station]['nsamples'] + params[station]['offset']
    if index > first_prediction_index:
        first_prediction_index = index
first_prediction = first_prediction_index * time_granularity

for date in dates:

    x = pd.DataFrame() # This matrix will include the features
    y = pd.DataFrame() # This matrix will include the target
    matrix = pd.DataFrame() # This matrix will store x and y

    print('[{}/{}] Processing {}...'.format(dates.index(date)+1, ndates, date))

    y = pd.read_csv(orig_folder + target_station + '/' + date + '_' + target_station + '.csv').round(decimal_pos)

    # print('$$$$$$$$$$ ' + target_station + ' $$$$$$$$$$')
    # print('TOTAL ROWS: {}\n'.format(len(y)))

    # We will skip intermediate samples for now
    y = y[first_prediction::time_granularity]
    last_prediction = y.last_valid_index()

    # print('FIRST PREDICTION: {}\nLAST PREDICTION: {}\nROWS: {}\n'.format(y.first_valid_index(), y.last_valid_index(), len(y)))

    max_dist = 0 #maximum time from nsamples and offset

    for station in stations:
        nsamples = params[station]['nsamples']
        offset = params[station]['offset']
        df = pd.read_csv(orig_folder + station + '/' + date + '_' + station + '.csv').round(decimal_pos)
        if max_dist < (nsamples + offset):
            max_dist = nsamples + offset

        # print('########## ' + station + ' ##########')
        # print('TOTAL ROWS: {}\n'.format(len(df)))

        for ns in range(nsamples):
            dist = (ns + offset + 1) * time_granularity
            first_sample = first_prediction - dist
            last_sample = last_prediction - dist
            if aggregation == 'skip':#TODO for having other processing methods like average selected in the config file
               # We will skip intermediate samples for now
               _x = df[first_sample:last_sample + time_granularity:time_granularity]
            # print('FIRST SAMPLE: {}\nLAST SAMPLE: {}\nROWS: {}\n'.format(_x.first_valid_index(), _x.last_valid_index(), len(_x)))
            # Rename column to include ghi/rel and ns
            col_name = station + rad_col + '_ns' + str(ns)
            _x = _x.rename(columns={station + rad_col: col_name})
            # Only radiation is needed. We need to reset the index in order to concatenate columns properly
            x = pd.concat([x,_x[col_name].reset_index(drop=True)], axis=1)

    # Rename column to include ghi/rel and target
    col_name = target_station + rad_col + '_target'
    y = y.rename(columns={target_station + rad_col: col_name})
    # Only radiation and sun position is needed. We need to reset the index in order to concatenate columns properly
    matrix = pd.concat([x,y[['az', 'el', col_name]].reset_index(drop=True)], axis=1)

    #WARNING: this will overwrite any existing CSV file with the same path and name
    matrix.to_csv(dest_folder + '_' + target_station + '_' + date + '_' + time_granularity + '_' + max_dist + '_'  + aggregation + '_' + dest_file_suffix, header=True, index=False)
