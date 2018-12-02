#!/usr/bin/env python3

#This file plots the percentage of test days with a negative skill

import os
import json
import pandas as pd
import sys
import optparse
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


def addOptions(parser):
    parser.add_option("--skill_test_config", default="",
              help="Config json file to select the models")

parser = optparse.OptionParser()
addOptions(parser)

(options,args) = parser.parse_args()

if not options.skill_test_config:
    print >> sys.stderr, "No config file specified\n'"
    sys.exit(1)

with open(options.skill_test_config, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

orig_folder = cfg_data['orig_folder']
out_folder = cfg_data['out_folder']
nn_type = cfg_data['nn_type']

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

files = os.listdir(orig_folder)

s='daily_skills_'
fp=[]
hp=[]
less_0=[]
for i in files:
    if i.startswith(s):
        report=pd.read_csv(orig_folder+i)
        fp_ = i[len(s):].partition(".")[0]
        fp.append(fp_)
        if fp_.endswith("min"):
            fpsec = int(int(fp_.replace('min','')) * 60)
        if fp_.endswith("s"):
            fpsec = int(int(fp_.replace('s','')))
        hp.append(fpsec)
        sk=report.skill
        less_0_ = sk[sk<0].count()
        less_0.append(round(less_0_/sk.count()*100,1))

hp, fp, less_0 = (list(t) for t in zip(*sorted(zip(hp, fp, less_0))))
plt.plot(hp,less_0)
plt.title('Percentage of test days with negative skill.\n'+nn_type)
plt.xticks(hp,fp,rotation='vertical')
plt.savefig(out_folder + 'negative_skill_test.png',bbox_inches = 'tight',dpi=300)
plt.close()


print('Plots created!')
