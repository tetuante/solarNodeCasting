#!/usr/bin/env python3

import pandas as pd
import json
import os
from pysolar.solar import *

with open('config.json', 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

t_columns = ['s', 'y', 'doy', 'hst']
sta_columns = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11',
             'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6',
             'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4',
             'ap7', 'dh6', 'dh7', 'dh8']

# Stations to consider
stations = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1',
            'ap6', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']
nstations = len(stations)

# Only consider data between 07:30 and 17:30 (HST)
initial_hour = 730
final_hour = 1729

input_folder = 'input'
output_folder = 'output'

input_files = os.listdir('input')
nfiles = len(input_files)

# Create output directory if it doesn't exist
for station in stations:
    folder = output_folder + '/' + station
    if not os.path.exists(folder):
        os.makedirs(folder)

for input_file in input_files:
    valid = True
    date = input_file.rstrip('.txt')
    input_path = input_folder + '/' + input_file
    print('[{}/{}] Reading {}...'.format(input_files.index(input_file)+1, nfiles, input_path))

    df = pd.read_csv(input_path, header=None, names=t_columns+sta_columns).round({station: 4 for station in sta_columns})

    # Take daylight data
    df = df[(df.hst >= initial_hour) & (df.hst <= final_hour)]

    if False in (df[stations] > 0).values:
        print('NOT VALID!')
        valid = False

    if valid:
        # Split data by date and station and add clear-sky radiation and radiation/clear-sky ratio
        for station in stations:
            lat = cfg_data['params'][station]['latitude']
            lon = cfg_data['params'][station]['longitude']

            # Take data corresponding to this station and reset the index
            sta_df = df[t_columns + [station]].reset_index(drop=True)

            # Convert time related columns to datetimes and store them in a new dataframe
            dt_df = pd.to_datetime(sta_df.s.apply(str) + ' ' + sta_df.y.apply(str) + ' ' + sta_df.doy.apply(str) + ' ' + sta_df.hst.apply(str), format='%S %Y %j %H%M')
            dt_df = dt_df.dt.tz_localize('HST')

            az_df = pd.DataFrame()
            el_df = pd.DataFrame()
            cs_df = pd.DataFrame()
            for datetime in dt_df:
                az_df = az_df.append({'az': get_azimuth(lat, lon, datetime)}, ignore_index=True)
                elevation = get_altitude(lat, lon, datetime)
                el_df = el_df.append({'el': elevation}, ignore_index=True)
                cs_df = cs_df.append({'cs': radiation.get_radiation_direct(datetime, elevation)}, ignore_index=True)

            sta_df = sta_df[station]

            sta_df = pd.concat([dt_df, az_df, el_df, sta_df, sta_df/cs_df['cs']], axis=1)
            sta_df.columns = ['hst datetime', 'az', 'el', station + '_ghi', station + '_rel']

            output_path = output_folder + '/' + station + '/' + date + '_' + station + '.csv'
            print('\n\t[{}/{}] Writing {}...'.format(stations.index(station)+1, nstations, output_path))
            sta_df.to_csv(output_path,header=True,index=False)
