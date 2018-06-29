#!/usr/bin/env python3

#This file adds the "derivative" for the nts.py. This derivative is just the variation between any consecutive sample


import pandas as pd
import numpy as np
import os
import optparse
import sys

#We have to provide just the folder where our matrices from nts.py are
def addOptions(parser):
   parser.add_option("--experimentFolder", default="",
             help="Folder where the matrices we want to manipulate are")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.experimentFolder:
   print >> sys.stderr, "No experiment folder specified\n"
   sys.exit(1)

input_folder = options.experimentFolder + '/'

input_files = []
in_files = os.listdir(input_folder)
for input_file in in_files:
  if input_file.endswith('.csv'):
    input_files.append(input_file)

if not os.path.exists(input_folder + 'derivative'):
    os.makedirs(input_folder + 'derivative')

for f in input_files:



    df = pd.read_csv(input_folder+f)
    x = df[df.columns[0:-1]] #Features.
    x_d = x.diff().round(5) #Features "derivative"
    x_d.iloc[0,:]=0
    #x_dd = x_d.diff().round(5) #Features "2nd derivative"
    #x_dd.iloc[0,:]=0
    x_d.columns = x_d.columns + '_der'
    #x_dd.columns = x_dd.columns + '_2der'

    x_d.to_csv(input_folder + 'derivative/' + f.replace('.csv','_der.csv'),header=True, index=False)
