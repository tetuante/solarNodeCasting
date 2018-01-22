#!/usr/bin/env python3

import pandas as pd
import os
import glob
import errno

t_names = ['s', 'y', 'doy', 'hst']
sta_names = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6', 'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']

stations = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'ap6', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8'] # Stations to consider
out_folder = 'output'

in_files = glob.glob('*.txt')

stations_df = {} # Dictionary containing a dataframe per station

# Create output directory if it doesn't exist and instantiate dataframes
for sta in stations:
    stations_df[sta] = pd.DataFrame()
    folder = out_folder + '/' + sta
    if not os.path.exists(folder):
        os.makedirs(folder)

for in_file in in_files:
    # We use dtype=str to avoid losing precision due to data type conversions
    df = pd.read_csv(in_file, header=None, names=t_names+sta_names, dtype=str)

    for sta in stations:
        stations_df[sta] = stations_df[sta].append(df[ t_names + [sta] ], ignore_index=True)

#WARNING: this will overwrite any axisting CSV file with the same path and name
for sta in stations_df:
    with open(out_folder + '/' + sta + '/' + sta + '.csv', 'w') as f:
        stations_df[sta].columns = t_names + ['ghi']
        stations_df[sta].to_csv(f,header=True,index=False)
