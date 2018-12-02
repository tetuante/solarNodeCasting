#!/usr/bin/env python3

#This file gets the coefficients for the linear regression and sorts it by absolute value
import pandas as pd
import numpy as np
import sys
import os
import json
import optparse
import time
from sklearn.externals import joblib
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

print('----\n')
print('Best features for linear regression.\n')
def addOptions(parser):
   parser.add_option("--LRfile", default="",
             help="Config json file for the data to pass to the model")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.LRfile:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

#with open('config.json', 'r') as cfg_file:
with open(options.LRfile, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)


matrix_folder = cfg_data['matrix_folder']
model_folder = cfg_data['model_folder']
dest_folder = cfg_data['dest_folder']

if not os.path.exists(dest_folder):
    os.makedirs(dest_folder)

#Loading X_test just for the header
X_test = pd.read_csv(matrix_folder+'/X_test.csv')

models = os.listdir(model_folder)
for i in models:
    if i.endswith('pkl'):
        csv_report = i[:-3] + 'csv'
    model = joblib.load(model_folder+i)
    importances = pd.DataFrame(model.coef_,index=X_test.columns,columns=['importance']).abs().sort_values('importance',ascending=False)
    importances.to_csv(dest_folder+csv_report)
