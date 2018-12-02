#!/usr/bin/env python3

#This file plots the skill using the best and worst features for LinReg and Random forests trained models.

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
n_features = cfg_data['n_features']
nn_type = cfg_data['nn_type']

if not os.path.exists(out_folder):
    os.makedirs(out_folder)

files = os.listdir(orig_folder)
bw = ['best','worst']
regtype = ['linreg','ranforest']


for i in bw:
    for j in regtype:
        hp=[]
        fp=[]
        skt=[]
        skv=[]
        filestart = i+'_'+j+'_'+n_features+'_features_for_'
        for k in files:
            if k.startswith(filestart):
                report=pd.read_csv(orig_folder+'/'+k)
                #worst_ranforest_5_features_for_15min_prediction_horizon_0.7_train_size_3_hidden_layers_with_300_300_300_neurons
                fp_ = k[len(filestart):].partition("_")[0]
                fp.append(fp_)
                skt.append(report.skill_train.values[0])
                skv.append(report.skill_validation.values[0])

                if fp_.endswith("min"):
                    fpsec = int(int(fp_.replace('min','')) * 60)
                if fp_.endswith("s"):
                    fpsec = int(int(fp_.replace('s','')))
                hp.append(fpsec)

        hp, skv, skt,fp = (list(t) for t in zip(*sorted(zip(hp, skv,skt, fp))))
        plt.plot(hp,skv,label='Validation skill')
        plt.plot(hp,skt,label='Train skill')
        plt.legend(loc='best', fancybox=True, framealpha=0.5)
        plt.title('Skill for train and validation sets.\n'+i+' '+n_features+' features for '+j+'\n'+nn_type)
        plt.xticks(hp,fp,rotation='vertical')
        plt.savefig(out_folder + '/skill_plot_for_'+i+'_'+j+'_'+n_features+'_features.png',bbox_inches = 'tight',dpi=300)
        plt.close()


print('Plots created!')
