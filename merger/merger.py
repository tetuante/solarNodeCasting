#!/usr/bin/env python3

import pandas as pd
import os

t_names = ['s', 'y', 'doy', 'hst']
sta_names = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6', 'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']

stations = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'ap6', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8'] # Stations to consider
in_folder = 'input'
out_folder = 'output'
nstations = len(stations)

# Only consider data between 07:30 and 17:30 (HST)
initial_hour = 730
final_hour = 1729

in_files = os.listdir('input')
nfiles = len(in_files)

# Create output directory if it doesn't exist and instantiate dataframes
for sta in stations:
    folder = out_folder + '/' + sta
    if not os.path.exists(folder):
        os.makedirs(folder)

for in_file in in_files:
    date = in_file.split('.')[0]
    in_path = in_folder + '/' + in_file
    print('[{}/{}] Reading {}...'.format(in_files.index(in_file)+1, nfiles, in_path))
    # We use dtype=str to avoid losing precision due to data type conversions
    df = pd.read_csv(in_path, header=None, names=t_names+sta_names, dtype={sta: str for sta in sta_names})
    # Take daylight data
    df = df.loc[(df['hst'] >= initial_hour) & (df['hst'] <= final_hour)]

    for sta in stations:
        out_path = out_folder + '/' + sta + '/' + date + '_' + sta + '.csv'
        print('\t[{}/{}] Writing {}...'.format(stations.index(sta)+1, nstations, out_path))
        df[t_names + [sta]].to_csv(out_path,header=True,index=False)
