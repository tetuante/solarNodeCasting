#!/usr/bin/env python3

#This file plots the relative GHI for every day and add our 5 different scores to it

import numpy as np
import pandas as pd
import json
import optparse
import os
import glob
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
import pylab
import dateutil
from datetime import datetime

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

stations = cfg_data["stations"]
time_granularity = cfg_data["time_granularity"]
orig_folder = cfg_data["orig_folder"]
dest_folder = cfg_data["dest_folder"]
dest_file = cfg_data["dest_file"]

for station in stations:
    curr_path = orig_folder + station
    in_files = os.listdir(curr_path)
    input_files = []
    for input_file in in_files:
        if input_file.endswith('.csv'):
            input_files.append(input_file)
    nfiles = len(input_files)
    scores = pd.read_csv(curr_path + '/scores/scores_' + station + '.csv')
    score_names = list(scores.columns.values)
    date_score = scores[scores.columns[0]]
    score_1 = scores[scores.columns[1]]
    score_2 = scores[scores.columns[2]]
    score_3 = scores[scores.columns[3]]
    score_4 = scores[scores.columns[4]]
    score_5 = scores[scores.columns[4]]



    if not os.path.exists(curr_path + dest_folder):
        os.makedirs(curr_path + dest_folder,exist_ok=True)
    else:
        print('Folder file already exists\n')

    for input_file in input_files:
        valid = True
        date = input_file.replace('_' + station + '.csv','')
        for i in range(len(date_score)):
            if str(date_score[i]) == date:
                score_index = i

        anio = date[0:4]
        mes = date[4:6]
        dia = date[6:8]
        input_path = curr_path + '/' +  input_file
        print('[{}/{}] Reading {}...'.format(input_files.index(input_file)+1,nfiles,input_path))


        df = pd.read_csv(input_path)

        x = df[0:len(df)  + time_granularity:time_granularity].reset_index(drop=True)

        ghi_rel = x[x.columns[-1]]
        dates = x[x.columns[0]].str[0:19] #Date and time
        times = pd.to_datetime(dates.values, format = '%Y-%m-%d %H:%M:%S') #In datetime format
        sc1 = str(round(score_1[score_index],4))
        sc2 = str(round(score_2[score_index],4))
        sc3 = str(round(score_3[score_index],4))
        sc4 = str(round(score_4[score_index],4))
        sc5 = str(round(score_5[score_index],4))


	#PLOT

        fig,ax = plt.subplots(1)
        fig.autofmt_xdate()
        plt.plot(times, ghi_rel, label='Relative GHI')
        xfmt = md.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        plt.axhline(1,color='red',label='Theoretical GHI') #ghi teorica = 1
        ax.legend(loc='best', fancybox=True, framealpha=0.5)
        plot_title = 'Theoretical vs Measured relative GHI\n'+dia+'-'+mes+'-'+anio
        sctxt1 = score_names[1] + ': ' + sc1 + '\n'
        sctxt2 = score_names[2] + ': ' + sc2 + '\n'
        sctxt3 = score_names[3] + ': ' + sc3 + '\n'
        sctxt4 = score_names[4] + ': ' + sc4 + '\n'
        sctxt5 = score_names[5] + ': ' + sc5 + '\n'
        sctxt = sctxt1+sctxt2+sctxt3+sctxt4+sctxt5
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.7,1.1,sctxt,transform=plt.gcf().transFigure,fontsize=10,verticalalignment='top',bbox=props)
        plt.title(plot_title,loc='left')
        plt.savefig(curr_path + dest_folder + date + '_' + station + '_' + dest_file,bbox_inches = 'tight')
        plt.close(fig)
