#!/usr/bin/env python3

#This file takes the raw data and creates new .csv's with relative radiation for individual stations

#This file uses the Page Clear Sky Model but not the Pysolar one as it contains some mistakes

import pandas as pd
import json
import os
import pysolar.util as util_csm
import pysolar.solar as solar
import pysolar.radiation as radiation
import math
import sys

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

if len(sys.argv) > 1:
    stations = [str(station) for station in sys.argv[1:]]
    nstations = len(sys.argv) - 1

for station in stations:
    if station not in sta_columns:
        raise NameError('Invalid station. Valid stations are:\n' + str(sta_columns))

# Only consider data between 07:30 and 17:30 (HST)
initial_hour = 730
final_hour = 1729

#Some parameters:
tem = 26.8           #Mean temperature in Hawaii in solar hours
pres = 1016.4        #Mean pressure in Hawaii in solar hours
AM = 2.0             # Default air mass is 2.0
TL = 1.0             # Default Linke turbidity factor is 1.0
SC = 1367.0          # Solar constant in W/m^2 is 1367.0. Note that this value could vary by +/-4 W/m^2
TY = 365             # Total year number from 1 to 365 days
elevation_default = 0.0      # Default elevation is 0.0



input_folder = 'input'
output_folder = 'ghi_output'

input_files = os.listdir('input')
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
            
            DOY = df.doy[0]
            # Take data corresponding to this station and reset the index
            sta_df = df[t_columns + [station]].reset_index(drop=True)

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
                altitude = solar.get_altitude(lat,lon, datetime)
                
                #FSOLALT (Page model):
                FSOLALT = 0.038175 + 1.5458 * math.sin(math.radians(altitude)) - 0.5998 * math.sin(math.radians(altitude)) ** 2

                #Diffuse Transmitance:
                DT = ((-21.657) + (41.752 * (TL)) + (0.51905 * (TL) * (TL)))

                #Optical Depth:
                OD = radiation.get_optical_depth(DOY)
                
                #Direct Irradiation under clear: DIRC:
                DIRC = SC * KD * math.exp(-0.8662 * AM * TL * OD) * math.sin(math.radians(altitude))

                #Diffuse Irradiation under clear sky: DIFFC:
              
                DIFFC = KD * DT * FSOLALT
                #Same thing as in DIRC, maybe the reference of the altitude has a phase shift
                ghi_csm = abs (DIRC) + abs(DIFFC)
                
                cs_df = cs_df.append({'cs': ghi_csm}, ignore_index=True)

            sta_df = sta_df[station]

            sta_df = pd.concat([dt_df, sta_df, sta_df/cs_df['cs']], axis=1)
            sta_df.columns = ['hst datetime', station + '_ghi', station + '_rel']

            output_path = output_folder + '/' + station + '/' + date + '_' + station + '.csv'
            print('        Writing ' + output_path + '...')
            sta_df.to_csv(output_path,header=True,index=False)

print('\nTotal input files: ' + str(nfiles))
print('    Ivalid files: ' + str(ninvalid))
print('    Valid files: ' + str(nfiles-ninvalid))
