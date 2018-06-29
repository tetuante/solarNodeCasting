#!/usr/bin/env python3

#After merging all the matrices it splits it into train&validation/test matrices


import os
import pandas as pd
import json
import optparse
import sys
import time
import numpy as np
from sklearn.model_selection import train_test_split

def addOptions(parser):
   parser.add_option("--NNconfigFile", default="",
             help="Neural Network config json file for the different parameters")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.NNconfigFile:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

#with open('config.json', 'r') as cfg_file:
with open(options.NNconfigFile, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

orig_folder = cfg_data['orig_folder']
dest_folder = cfg_data['dest_folder']
der_folder = cfg_data['der_folder']
derivative = cfg_data['derivative']
scores_file = cfg_data['scores_file']
scores_threshold = cfg_data['scores_threshold'] #we set 25% as our default threshold and get the score for it


input_files=[]
input_files_dates=[]
in_files = os.listdir(orig_folder)
for input_file in in_files:
    if input_file.endswith('.csv'):
        input_files.append(input_file)

#We remove the vulcan activity &/or weird days:

scores = pd.read_csv(scores_file)

scores_days = scores[scores.columns[0]]
scores_25 = scores[scores.columns[2]]
#Now we get... 
scores_25_index = scores_25.index.values
days_25 = scores_25_index[scores_25 > scores_threshold]

#And then we end up with a list of days (int)

bad_days = scores_days[days_25]
days_list = [] #in str
for i in bad_days:
    days_list.append(str(i))

#Finally we remove our bad days and end up with "kind of good" days (at least days with the same behaviour, we think)
for d in days_list:
    for f in input_files:
        if d in f:
            input_files.remove(f)


lenfiles = len(input_files)
input_der_files = []
if derivative == True:
    print('derivative TRUE\n')
    for i in input_files:
        input_der_files.append(der_folder + i.replace('.csv','_der.csv'))
else:
    print('derivative FALSE\n')
tv = dest_folder + '/train_validation'
train = dest_folder + '/train_validation/train'
validation = dest_folder + '/train_validation/validation'
test = dest_folder + '/test'

if not os.path.exists(train):
    os.makedirs(train)
if not os.path.exists(tv):
    os.makedirs(tv)
if not os.path.exists(validation):
    os.makedirs(validation)
if not os.path.exists(test):
    os.makedirs(test)

X = pd.DataFrame()
Y = pd.DataFrame()

#Randomize days:


arr_days = np.arange(lenfiles)
ran_seed = 42 #our seed to randomize data
np.random.seed(ran_seed)
np.random.shuffle(arr_days)

lenfiles_test = int(round(lenfiles * 0.15,0))
arr_rand_test = arr_days[0:lenfiles_test]

lenfiles_train = lenfiles - lenfiles_test
arr_rand_train = arr_days[lenfiles_test:]



input_files_test = []
input_files_train = []

for i in arr_rand_test:
    input_files_test.append(input_files[i])

for i in arr_rand_train:
    input_files_train.append(input_files[i])

print('Appending {} test files\n'.format(lenfiles_test))
start_time = time.time()
for f in input_files_test:
    df = pd.read_csv(orig_folder + '/' + f)
    x = df[df.columns[0:-1]].round(5)
    y = df[df.columns[-1]].round(5)
    if derivative == True:
        f_der = f.replace('.csv','_der.csv')
        d = pd.read_csv(der_folder + '/' + f_der).round(5)
        x = pd.concat([x,d],axis=1)

    X = pd.concat([X,x],ignore_index=True)
    Y = pd.concat([Y,y],ignore_index=True)

X.to_csv(test+'/X_test.csv',header=True,index=False)
Y.to_csv(test+'/Y_test.csv',header=True,index=False)

end_time = time.time()
print('{} files appended in {} seconds. Splitting matrices.\n'.format(lenfiles_test,end_time-start_time))

X = pd.DataFrame()
Y = pd.DataFrame()
print('Appending {} train and validation files\n'.format(lenfiles_train))
start_time = time.time()
for f in input_files_train:
    df = pd.read_csv(orig_folder + '/' + f)
    x = df[df.columns[0:-1]].round(5)
    y = df[df.columns[-1]].round(5)
    if derivative == True:
        f_der = f.replace('.csv','_der.csv')
        d = pd.read_csv(der_folder + '/' + f_der).round(5)
        x = pd.concat([x,d],axis=1)

    X = pd.concat([X,x],ignore_index=True)
    Y = pd.concat([Y,y],ignore_index=True)


X.to_csv(tv+'/X_tr_val.csv',header=True,index=False)
Y.to_csv(tv+'/Y_tr_val.csv',header=True,index=False)

end_time = time.time()
print('{} files appended in {} seconds. Splitting matrices.\n'.format(lenfiles_train,end_time-start_time))
