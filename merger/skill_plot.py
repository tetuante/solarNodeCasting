#!/usr/bin/env python3

#This file plots the skill vs forecast prediction

import os
import json
import pandas as pd
import sys
import optparse
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


def addOptions(parser):
    parser.add_option("--skill_plot_config", default="",
              help="Config json file to select the models")

parser = optparse.OptionParser()
addOptions(parser)

(options,args) = parser.parse_args()

if not options.skill_plot_config:
    print >> sys.stderr, "No config file specified\n'"
    sys.exit(1)

with open(options.skill_plot_config, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

orig_folder = cfg_data['orig_folder']
out_folder = cfg_data['out_folder']
nn_type = cfg_data['nn_type']
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

f=os.listdir(orig_folder)
for i in f:
    if i.startswith('scores'):
        orig_file=orig_folder+'/'+i
report = pd.read_csv(orig_file)

fp = report.forecast_prediction
skt = report.skill_train
skv = report.skill_validation
hp=[]
for i in fp:
    if i.endswith("min"):
        fp_sec = int(int(i.replace('min','')) * 60)
    if i.endswith("s"):
        fp_sec = int(int(i.replace('s','')))
    hp.append(fp_sec)

#plot
plt.plot(hp,skv.values,label='Validation skill')
plt.plot(hp,skt.values,label='Train skill')
plt.legend(loc='best', fancybox=True, framealpha=0.5)
plt.title('Skill for train and validation sets.\n'+nn_type)
plt.xticks(hp,fp,rotation='vertical')
plt.savefig(out_folder + '/skill_plot.png',bbox_inches = 'tight',dpi=300)
plt.close()
