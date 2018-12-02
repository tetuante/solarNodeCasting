#!/usr/bin/env python3

#This file compares the best and worst features for LinReg and Random forests trained models.

import os
import json
import pandas as pd
import sys
import optparse

def addOptions(parser):
    parser.add_option("--common_config", default="",
              help="Config json file to select the models")

parser = optparse.OptionParser()
addOptions(parser)

(options,args) = parser.parse_args()

if not options.common_config:
    print >> sys.stderr, "No config file specified\n'"
    sys.exit(1)

with open(options.common_config, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

linreg_folder = cfg_data['linreg_folder'] #where the linreg models are
rf_folder = cfg_data['rf_folder'] #where the random forest models are
num_features = cfg_data['num_features'] #how many features we're taking
stations = cfg_data['stations'] #which stations were taking into the training
out_folder = cfg_data['out_folder']


if not os.path.exists(out_folder):
    os.makedirs(out_folder)

linreg_models = os.listdir(linreg_folder)
rf_models = os.listdir(rf_folder)

linreg_text = "linear_regression_stations_" + stations + "_for_"
rf_text = "random_forest_regressor_for_stations_" + stations + "_for_"
lr_len = len(linreg_text)
rf_len = len(rf_text)

print("opening reports\n")
for i in linreg_models:
    forecast = i[lr_len:].partition("_")[0]
    print('forecast: {}.\n-----\n'.format(forecast))
    lr = pd.read_csv(linreg_folder + i)
    lr = lr[lr.columns[0]]
    lr_best = lr[:num_features]
    lr_worst = lr[(-1)*num_features:].reset_index(drop=True)
    print('Best feature: {}\n'.format(lr_best.values[0]))
    for h in rf_models:
        fc_rf = h[rf_len:].partition("_")[0]
        if fc_rf == forecast:
            rf = pd.read_csv(rf_folder + h)
            rf = rf[rf.columns[0]]
            rf_best = rf[:num_features]
            rf_worst = rf[(-1)*num_features:].reset_index(drop=True)
            common = pd.DataFrame({'best_linreg':lr_best,'best_ranforest':rf_best,
                                   'worst_linreg':lr_worst,'worst_ranforest':rf_worst})
            common.to_csv(out_folder + 'best_worst_' + str(num_features) + '_features_' + forecast + '.csv',header=True,index=False)
            print('Common file for {} forecast completed!\n'.format(forecast))
