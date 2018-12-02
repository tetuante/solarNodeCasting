#!/usr/bin/env python3

#This file applies the random forest regression models to the test days
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
from sklearn import tree



def addOptions(parser):
   parser.add_option("--RFRfile", default="",
             help="Config json file for the data to pass to the model")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.RFRfile:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

#with open('config.json', 'r') as cfg_file:
with open(options.RFRfile, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)


orig_folder = cfg_data['orig_folder']
model_folder = cfg_data['model_folder']
dest_folder = cfg_data['dest_folder']

#Train model parameters:

train_size = cfg_data['train_size'] # from 0.1 to 0.7. Ideally 0.7
feature_values = cfg_data['features'] #[['dh3'], ['dh3','dh4','dh5','dh10','ap1'], ['all']]. Ideally 'all'
testing_days = cfg_data['testing_days'] #how many days do we want to test. int. Like 4/5 days.
depth_values = cfg_data['depth'] 
hor_pred = cfg_data['hor_pred'] #folder_names




out_folder = orig_folder + dest_folder

if not os.path.exists(out_folder):
    os.makedirs(out_folder)


print('Loading dataframes...\n')
load_start = time.time()
x_original = pd.read_csv(orig_folder+'/X_tr_val.csv')
y_original = pd.read_csv(orig_folder+'/Y_tr_val.csv')
load_end = time.time()
load_time = load_end - load_start
load_min = int(load_time / 60)
load_sec = load_time % 60
print('Dataframes loaded in {} minutes {} seconds!\n'.format(load_min,load_sec))

split_start = time.time()
#We get the number of days
lenrow_original = len(x_original.values)
day_length = 7170 #36000/5(our time_granularity) = 7200 but we lose half a minute in the nts.py due to offset,nsamples, etc
days = int((lenrow_original / day_length))
print('Days: {}\n'.format(days))

#Since it's already been randomized in the previous nn_splits.py there's no need to do it again.
arr_days = np.arange(days)
ran_seed = 42 #our seed to randomize data
np.random.seed(ran_seed)
np.random.shuffle(arr_days)
len_days_validation = int(round(days * 0.176470588,0))
days_validation = arr_days[0:len_days_validation]
days_train = arr_days[len_days_validation:]

#Now we take random DAYS for train and validation:
x_train = pd.DataFrame()
y_train = pd.DataFrame()
x_val_original = pd.DataFrame()
y_val_original = pd.DataFrame()
for day in days_train:
    x_train = pd.concat([x_train,x_original.iloc[day:day+day_length]],ignore_index=True)
    y_train = pd.concat([y_train,y_original.iloc[day:day+day_length]],ignore_index=True)
for day in days_validation:
    x_val_original = pd.concat([x_val_original,x_original.iloc[day:day+day_length]],ignore_index=True)
    y_val_original = pd.concat([y_val_original,y_original.iloc[day:day+day_length]],ignore_index=True)

lencol = len(x_train.columns) #number of columns for x
lenrow = len(x_train.values)
split_end = time.time()
split_time = split_end - split_start
split_min = int(split_time / 60)
split_sec = split_time % 60
print('Splitting completed in {} minutes {} seconds. Length for train: {}\n'.format(split_min,split_sec,len(y_train)))



#Since we configured our matrices with an offset we have to adjust to "jump" to the sample we want to actually predict
offset_samples = 15

for hp in hor_pred:
    hor_pred_indices = int(int(hp.replace('min','')) * 60 / 5 - offset_samples) #amount of indices we'll move. 5 because it's our time granularity.
    print('hor_pred_indices: {} \n'.format(hor_pred_indices))

#TRAIN SIZE:

    for ts in train_size:

        seed=23 #we can change it if we want, just giving this value
        n_rows = int(lenrow*ts)
        print('Taking less samples for train size = {}. y length: {} \n'.format(ts,n_rows))
        y = y_train.sample(n_rows,random_state=seed)
        y_index = y.index.values
        y_index_valid = y_index[(y_index % day_length) < (day_length - hor_pred_indices)] #so we don't get values for the previous or next day

        print('Building randomized y matrix with valid indices...\n')
        y = np.ravel(y_original.iloc[y_index_valid + hor_pred_indices])
        print('Building y matrix removing invalid indices for persistence model...\n')
        y_pred_persistence = np.ravel(y_original.iloc[y_index_valid])

        y_val_index = y_val_original.index.values
        y_val_index_valid = y_val_index[(y_val_index %36000) > hor_pred_indices]
        y_pred_persistence_val = np.ravel(y_original.iloc[y_val_index_valid])
        print('Building X matrix...Same thing as before...\n')
        x = x_original.iloc[y_index_valid] #like our randomization but just picking the same indices
        x_val = x_original.iloc[y_val_index_valid]
        y_val = np.ravel(y_original.iloc[y_val_index_valid + hor_pred_indices])
             
        
        for ft in feature_values:
            X = pd.DataFrame()
            X_val = pd.DataFrame()
            if ft[0] == 'all':
                X = x
                X_val = x_val
            else:
                print('there is a problem with the ft==all thingy...\n')
                for n in range(len(ft)):
                    for i in range(lencol):
                        if x.columns[i].startswith(ft[n]):
                            X = pd.concat([X,x[x.columns[i]]],axis=1,ignore_index=True)
                            X_val = pd.concat([X_val,x_val[x_val.columns[i]]],axis=1,ignore_index=True)

            stations = ''
            if ft[0] == 'all':
                stations = ft[0] + ' ' 
            else:
                for sta in ft:
                    stations = stations + sta + ' '
            sts = stations.replace(' ','_')
            prcnt = ts

            if depth_values == 0:
                output_text = '/random_forest_regressor_for_stations_' + sts + 'for_' + hp + '_prediction_horizon_' + str(prcnt) + '_train_size_default_depth'
            else:
                output_text = '/random_forest_regressor_for_stations_' + sts + 'for_' + hp + '_prediction_horizon_' + str(prcnt) + '_train_size_' + str(depth_values) + '_depth'


            model_filename = model_folder + output_text + '.pkl'
            clf = joblib.load(model_filename)
            print('Predicting...\n')
            pred_start = time.time()
            print('Validating...\n')
            y_pred_val = clf.predict(X_val)
            pred_end = time.time()
            pred_time = pred_end - pred_start
            print('Predicted in {} seconds.\n'.format(int(pred_time)))
                

            y_df = pd.DataFrame()
            for d in range(testing_days):
                y_day = y_val[d*day_length:d*day_length+day_length]
                y_pred_day = y_pred_val[d*day_length:d*day_length+day_length]
                y_persistence_day = y_pred_persistence_val[d*day_length:d*day_length+day_length]
                print('Saving figures\n')
                #SAVING FIGURES FOR FIRST SCORE:
                plt.figure()
                plt.plot(y_day,label='Real')
                plt.plot(y_pred_day,label='Predicted')
                plt.plot(y_persistence_day,label='Persistence model')
                plt.legend(loc='best', fancybox=True, framealpha=0.5)
                plt.title('Predicted and real relative values for random_forest. Train subset.')
                plt.savefig(out_folder + output_text + '_day_' + str(d) + '.png',bbox_inches = 'tight')
                plt.close()
                print('Building .csv')
                y_day_df = pd.DataFrame(y_day)
                y_pred_day_df = pd.DataFrame(y_pred_day)
                y_persistence_day_df = pd.DataFrame(y_persistence_day)
                y_df = pd.concat([y_day_df,y_pred_day_df, y_persistence_day_df],axis=1)
                y_df.columns = ['real','predicted','persistence']
                y_df.to_csv(out_folder + output_text + '_day' + str(d) + '.csv', header=True,index=False)
                print('Day finished!\n')
