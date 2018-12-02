#!/usr/bin/env python3

#This file takes the raw data and creates new .csv's with relative radiation for individual stations


import pandas as pd
import json
import os
import pysolar.util as util_csm
import pysolar.solar as solar
import pysolar.radiation as radiation
import math
import sys

def addOptions(parser):
   parser.add_option("--config", default="",
             help="Config json file for the data to pass to the model")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.config:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

with open(options.config, 'r') as cfg_file:
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

if len(sys.argv) > 1:
    stations = [str(station) for station in sys.argv[1:]]
    nstations = len(sys.argv) - 1

for station in stations:
    if station not in sta_columns:
        raise NameError('Invalid station. Valid stations are:\n' + str(sta_columns))

# Ideally only consider data between 07:30 and 17:29 (HST) to get always sunlight
initial_hour = cfg_data['initial_hour']
final_hour = cfg_data['final_hour']

simple_csm = cfg_data['csm']

input_folder = cfg_data['orig_folder']
output_folder = cfg_data['dest_folder'] + '_' + simple_csm

input_files = os.listdir(input_folder)
nfiles = len(input_files)

# Create output directory if it doesn't exist
for station in stations:
    folder = output_folder + '/' + station
    if not os.path.exists(folder):
        os.makedirs(folder)

ninvalid = 0 # Number of files that have negative values

for input_file in input_files:
    valid = True
    date = input_file.rstrip('.txt')
    input_path = input_folder + '/' + input_file
    print('[{}/{}] Reading {}...'.format(input_files.index(input_file)+1, nfiles, input_path), end = ' ')

    df = pd.read_csv(input_path, header=None, names=t_columns+sta_columns).round({station: 4 for station in sta_columns})

    # Take daylight data
    df = df[(df.hst >= initial_hour) & (df.hst <= final_hour)]

    # Validate data: we will skip this input_file if it contains negative data or
    # if any measurement is missing
    if False in (df[stations] > 0.0).values:
        print('Negative values were found... We will skip this day')
        ninvalid += 1
        valid = False

    if valid:
        print('Data seem valid!')
        # Split data by date and station and add clear-sky radiation and radiation/clear-sky ratio
        for station in stations:
            print('    [{}/{}] Processing station {}...'.format(stations.index(station)+1, nstations, station))
            lat = cfg_data['params'][station]['latitude']
            lon = cfg_data['params'][station]['longitude']
            
            # Take data corresponding to this station and reset the index
            sta_df = df[t_columns + [station]].reset_index(drop=True)
            DOY = sta_df.doy[0]

            # Convert time related columns to datetimes and store them in a new dataframe
            dt_df = pd.to_datetime(sta_df.s.apply(str) + ' ' + sta_df.y.apply(str) + ' ' + sta_df.doy.apply(str) + ' ' + sta_df.hst.apply(str), format='%S %Y %j %H%M')
            dt_df = dt_df.dt.tz_localize('HST') # This sets tzinfo to HST
            # dt_df = dt_df.dt.tz_convert(None) # This converts time to UTC and removes tzinfo

            az_df = pd.DataFrame()
            el_df = pd.DataFrame()
            cs_df = pd.DataFrame()
            for datetime in dt_df:
                KD = util_csm.mean_earth_sun_distance(datetime)
                DEC = util_csm.declination_degree(datetime,TY)
                altitude = solar.get_altitude(lat,lon,datetime)
                azimuth = solar.get_azimuth(lat,lon,datetime)

                if simple_csm == 'kasten':
                    ghi_csm = 910 * math.sin(math.radians(altitude))
                if simple_csm == 'haurwitz':
                    ghi_csm = 1098 * math.sin(math.radians(altitude)) * math.exp(-0.057 / (math.sin(math.radians(altitude))))
                
                cs_df = cs_df.append({'cs': ghi_csm}, ignore_index=True)
                el_df = el_df.append({'elevation':altitude}, ignore_index=True)
                az_df = az_df.append({'azimuth': azimuth}, ignore_index=True)

            sta_df = sta_df[station]

            sta_df = pd.concat([dt_df, sta_df, el_df, az_df, sta_df/cs_df['cs']], axis=1)
            sta_df.columns = ['hst datetime', station + '_ghi', 'elevation', 'azimuth', station + '_rel']

            output_path = folder + '/' + date + '_' + station + '.csv'
            print('        Writing ' + output_path + '...')
            sta_df.to_csv(output_path,header=True,index=False)

print('\nTotal input files: ' + str(nfiles))
print('    Ivalid files: ' + str(ninvalid))
print('    Valid files: ' + str(nfiles-ninvalid))
