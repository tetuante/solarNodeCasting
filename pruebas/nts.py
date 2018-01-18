#!/usr/bin/env python3

import json
import pandas as pd
import os
import glob
import errno
import numpy as np

with open('config.json', 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

stations = cfg_data['input_sta']
dest_folder = cfg_data['dest_folder']
dest_file = cfg_data['dest_file']

nsamples = cfg_data['nsamples'] #number of samples, we'll start from [(t-nsamples*ntime) - offset*ntime]
ntime = cfg_data['ntime'] #time for every sample
offset = cfg_data['offset'] #we''ll skip this sample

predictiont = cfg_data['predictiont'].split(' ')

original_column_names = cfg_data['original_column_names']

time = predictiont[0].split(':')
hst = time[0] + time[1]
s = time[2][0].lstrip('0') + time[2][1]
doy = predictiont[1]
y = predictiont[2]

if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

#This will be the matrix with all the GHIs
X = pd.DataFrame()

for station in stations:
    df = pd.read_csv(station,header=None,names=original_column_names, dtype=str)
    ghi = df['ghi']

    predictiont_index = df.loc[(df['hst'] == hst) & (df['s'] == s) & (df['doy'] == doy) & (df['y'] == y)].index[0]
    print('predictiont_index: {}'.format(predictiont_index))
    if ((predictiont_index - nsamples * ntime - offset * ntime) < 0):
        raise NameError('Error, try a bigger starting time or less samples')
    #This will be the matrix with all the GHIs for the current station:
    x = pd.DataFrame()
    #Adding columns for the 1st station
    #OK, it's inside a loop that will put the 2nd station later...
    #That's what I wanted from the beginning

    for i in range(nsamples):
        A = pd.DataFrame()
        B = pd.DataFrame()
        pos = predictiont_index - (offset + nsamples - i) * ntime
        gg = ghi[pos:predictiont_index+ntime*i:ntime]
        A = A.append(gg,ignore_index = True)
        A = A.T
        B = B.append(A,ignore_index = True)
        # X = X.append(gg, ignore_index = True) #Nope. Append adds in same column, not new one
        #X = X.insert(j,j,gg.values,allow_duplicates = True) #Nooope
        x = pd.concat([x,B], ignore_index = True, axis = 1)

    #x = pd.concat([AZ, EL, x], ignore_index = True, axis = 1)
    X = pd.concat([X,x], ignore_index = True, axis = 1)

with open(dest_folder + dest_file,'w') as f:
    X.to_csv(f,header=False,index=False)
