#!/usr/bin/env python3

#This file creates different metrics for every day in an approach to get how similar to the CSM day it was

import pandas as pd
import numpy as np
import json
import os
import sys
import optparse

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


orig_folder = cfg_data['orig_folder']
dest_folder = cfg_data['dest_folder']
time_granularity = cfg_data['time_granularity']
threshold_1 = cfg_data['threshold_1']
threshold_2 = cfg_data['threshold_2']
threshold_3 = cfg_data['threshold_3']
stations = cfg_data['stations']
#orig_path = os.getcwd()

for station in stations:
    #curr_path = orig_path + orig_folder + '/' + station
    curr_path = orig_folder + '/' + station
    input_files = os.listdir(curr_path)

    scores = pd.DataFrame()
    #date_df = pd.DataFrame()

    for input_file in input_files:
        date = input_file.replace('_' + station + '.csv','')
        df = pd.read_csv(curr_path + '/' + input_file)
        ghi = df[0:len(df) + time_granularity:time_granularity]
        ghi_rel = ghi[ghi.columns[-1]]
        err_1 = 0
        score_1 = 0
        score_2 = 0
        score_3 = 0
        score_4 = 0
        #SCORE 1:
        ghi_max = ghi_rel.max()
        if ghi_max > 1:
            for i in range(len(ghi_rel)):
                err_1 = abs((ghi_max - ghi_rel[i]))
                score_1 = score_1 + err_1
        else:
            for i in range(len(ghi_rel)):
                err_1 = abs((1 - ghi_rel[i]))
                score_1 = score_1 + err_1

        #SCORE 2:

        for i in range(len(ghi_rel)):
            if ghi_rel[i] < threshold_1:
                score_2 += 1

        #SCORE 3:

        for i in range(len(ghi_rel)):
            if ghi_rel[i] < threshold_2:
                score_3 += 1

        #SCORE 4:

        for i in range(len(ghi_rel)):
            if ghi_rel[i] < threshold_3:
                score_4 += 1


        score_1 = score_1 / len(ghi_rel)
        score_2 = score_2 / len(ghi_rel)
        score_3 = score_3 / len(ghi_rel)
        score_4 = score_4 / len(ghi_rel)


        #date_df = pd.to_datetime(date, format='%Y%m%d')
        scores = scores.append({"date":date,"score_1":score_1,"score_threshold_"+str(threshold_1):score_2,"score_threshold_"+str(threshold_2):score_3,"score_threshold_"+str(threshold_3):score_4},ignore_index=True)

    scores.to_csv(curr_path + '/' + 'scores_' + station + '.csv', header=True, index=False)
    print("Finished station " + station )
