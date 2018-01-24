#!/usr/bin/env python3

import pandas as pd
import os
import glob

t_names = ['s', 'y', 'doy', 'hst']
sta_names = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6', 'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']

stations = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'ap6', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8'] # Stations to consider
in_folder = 'input'
out_folder = 'output'
nstations = len(stations)

# Only consider data between 08:00 and 15:59 (HST)
initial_hour = 800
final_hour = 1559

in_files = glob.glob(in_folder + '/' + '*.txt')
nfiles = len(in_files)

stations_df = {} # Dictionary containing a dataframe per station

# Create output directory if it doesn't exist and instantiate dataframes
for sta in stations:
    stations_df[sta] = pd.DataFrame()
    folder = out_folder + '/' + sta
    if not os.path.exists(folder):
        os.makedirs(folder)

for in_file in in_files:
    print('[{}/{}] Reading {}...'.format(in_files.index(in_file)+1, nfiles, in_file))
    # We use dtype=str to avoid losing precision due to data type conversions
    df = pd.read_csv(in_file, header=None, names=t_names+sta_names, dtype={sta: str for sta in sta_names})

    df = df.loc[(df['hst'] >= initial_hour) & (df['hst'] <= final_hour)]

    for sta in stations:
        stations_df[sta] = stations_df[sta].append(df[ t_names + [sta] ], ignore_index=True)

#WARNING: this will overwrite any existing CSV file with the same path and name
for sta in stations_df:
    csv = out_folder + '/' + sta + '/' + sta + '.csv'
    with open(csv, 'w') as f:
        print('[{}/{}] Writing {}...'.format(stations.index(sta)+1, nstations, csv))
        stations_df[sta].columns = t_names + [sta]
        stations_df[sta].to_csv(f,header=True,index=False)
