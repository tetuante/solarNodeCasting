#!/usr/bin/env python3

import pandas
import os
import glob
import errno

t_names = ['s', 'y', 'doy', 'hst']
sta_names = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6', 'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']
out_folder = 'output'

in_files = glob.glob('*.txt')

# Create output directory if it doesn't exist
for sta in sta_names:
    folder = out_folder + '/' + sta
    if not os.path.exists(folder):
        os.makedirs(folder)

for in_file in in_files:
    # We use dtype=str to avoid losing precision due to data type conversions
    df = pandas.read_csv(in_file, header=None, names=t_names+sta_names, dtype=str)

    for sta in sta_names:
        sta_df = df[ t_names + [sta] ]

        # WARNING: This will append the dataframe to the CSV file even if it already exists before running this script
        with open(out_folder + '/' + sta + '/' + sta + '.csv', 'a') as f:
            sta_df.to_csv(f,header=False,index=False)
