#!/usr/bin/env python3

#This file creates the trained models for a given neural network configuration

import pandas as pd
import numpy as np
import sys
import os
import json
import optparse
import time
from sklearn.neural_network import MLPRegressor
from sklearn.externals import joblib
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt



def addOptions(parser):
   parser.add_option("--NNfile", default="",
             help="Config json file for the data to pass to the model")

parser = optparse.OptionParser()
addOptions(parser)

(options, args) = parser.parse_args()

if not options.NNfile:
   print >> sys.stderr, "No configuration file specified\n"
   sys.exit(1)

#with open('config.json', 'r') as cfg_file:
with open(options.NNfile, 'r') as cfg_file:
    cfg_data = json.load(cfg_file)

orig_folder = cfg_data['orig_folder']
dest_folder = cfg_data['dest_folder']

train_size = cfg_data['train_size'] # [1/7, 2/7, 3/7, 4/7, 5/7, 6/7, 7/7]
hor_pred = cfg_data['hor_pred'] #folder_names
alpha_values = cfg_data['alpha'] #[0.0001, 0.001, 0.01, 0,1]
feature_values = cfg_data['features'] #[['dh3'], ['dh3','dh4','dh5','dh10','ap1'], ['all']]
hls = cfg_data['hls'] #we pass it as a list or int

if isinstance(hls,list):
    hls=tuple(hls)



out_folder = orig_folder + dest_folder
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

model_folder = out_folder+'/models'
if not os.path.exists(model_folder):
    os.makedirs(model_folder)

csvs_folder = out_folder+'/csvs'
if not os.path.exists(csvs_folder):
    os.makedirs(csvs_folder)

graphs_folder = out_folder+'/graphs'
if not os.path.exists(graphs_folder):
    os.makedirs(graphs_folder)


print('Loading dataframes...\n')
load_start = time.time()
x_original = pd.read_csv(orig_folder+'/X_tr_val.csv')
y_original = pd.read_csv(orig_folder+'/Y_tr_val.csv')
load_end = time.time()
load_time = load_end - load_start
load_min = int(load_time / 60)
load_sec = load_time % 60
print('Dataframes loaded in {} minutes {} seconds! Splitting for train and validation...\n'.format(load_min,load_sec))

split_start = time.time()
#We get the number of days and split for train and validation
lenrow_original = len(x_original.values)
#day_length = 7170 #36000/5(our time_granularity) = 7200 but we lose half a minute in the nts.py due to offset,nsamples, etc

day_length=1200 #fou our 30 seconds time granularity

days = int((lenrow_original / day_length))
print('Days: {}\n'.format(days))
print('Days(integer): {}\n'.format(int(days)))

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
print('Splitting completed in {} minutes {} seconds. Length for train: {}\n'.format(split_min,split_sec,y_train))


#Since we configured our matrices with an offset we have to adjust to "jump" to the sample we want to actually predict

for hp in hor_pred:
    hor_pred_indices = int(int(hp.replace('min','')) * 60 / 5) #amount of indices we'll move. 5 because it's our time granularity.


#TRAIN SIZE:

    for ts in train_size:

        seed=23 #we can change it if we want, just giving this value
        n_rows = int(lenrow*ts)
        print('Taking less samples for train size = {}. y length: {} \n'.format(ts,n_rows))
        y = y_train.sample(n_rows,random_state=seed)
        y_index = y.index.values
        y_index_valid = y_index[(y_index % day_length) < (day_length - hor_pred_indices)] #so we don't get values for the previous or next day
        y_indices_lost = len(y_index) - len(y_index)
        print('Indices computed. {} indices lost \n.'.format(y_indices_lost))
        print('Building randomized y matrix with valid indices...\n')
        y = np.ravel(y_original.iloc[y_index_valid + hor_pred_indices])
        print('Building y matrix removing invalid indices for persistence model...\n')
        y_pred_persistence = np.ravel(y_original.iloc[y_index_valid])

        y_val_index = y_val_original.index.values
        y_val_index_valid = y_val_index[(y_val_index % day_length) < (day_length - hor_pred_indices)]
        y_pred_persistence_val = np.ravel(y_val_original.iloc[y_val_index_valid])
        print('Building X matrix...Same thing as before...\n')
        x = x_original.iloc[y_index_valid] #like our randomization but just picking the same indices
        x_val = x_val_original.iloc[y_val_index_valid]
        y_val = np.ravel(y_val_original.iloc[y_val_index_valid + hor_pred_indices])
#STATIONS TO SELECT:

        for ft in feature_values:
            X = pd.DataFrame()
            X_val = pd.DataFrame()
            
            if ft[0] == 'all':
                X = x
                X_val = x_val
            else:
                for n in range(len(ft)):

                    for i in range(lencol):

                        if x.columns[i].startswith(ft[n]):

                            X = pd.concat([X,x[x.columns[i]]],axis=1,ignore_index=True)
                            X_val = pd.concat([X_val,x_val[x_val.columns[i]]],axis=1,ignore_index=True)

            scrs = []
            scrs_val = []
            k1_train_scores = []
            k1_validation_scores = []
            kc_train_scores = []
            kc_validation_scores = []
            k1_kc_train_scores = []
            k1_kc_validation_scores = []

            if isinstance(hls,tuple) == False:
                 if hls > 10:
                    neurons = (hls,)
                    len_hls = '1'

            if isinstance(hls,tuple) == False:
                if hls == 1:
                     neurons = int(len(X.columns)/2 + 1)
                     hls = (neurons,)
                     len_hls = '1'

            if isinstance(hls,tuple) == False:
                if hls == 2:
                     neurons = int(len(X.columns)/2 + 1)
                     hls = (neurons,neurons)
                     len_hls = '2'

            if isinstance(hls,tuple) == False:                    
                if hls == 3:
                     neurons = int(len(X.columns)/2 + 1)
                     hls = (neurons,neurons,neurons)
                     len_hls = '3'

            else:
                len_hls = str(len(hls))
            
            hls_str = str(hls).replace('(','_').replace(', ','_').replace(')','_')
            hls_neurons_str = ''
            for i in range(len(hls)):
                hls_neurons_str = hls_neurons_str + str(hls[i])+'_'

            for av in alpha_values:



                stations = ''
                if ft[0]=="all":
                    stations = "all "
                else:
                    for sta in ft:
                        stations = stations + sta + ' '
                sts = stations.replace(' ','_')
                prcnt = round(ts*0.7,2)



                output_text = '/stations_' + sts + 'for_' + hp + '_prediction_horizon_' + str(prcnt) + '_train_size_' + len_hls + '_hidden_layers_with_' + hls_neurons_str + 'neurons'
 
                print('Creating MLPregressor\n')
                nn_model = MLPRegressor(hidden_layer_sizes=hls,alpha=av)
                print('Fitting...\n'+output_text+'\n')
                fit_start = time.time()
                nn_model.fit(X,y)
                fit_end = time.time()
                fit_time = fit_end - fit_start
                fit_min = int(fit_time / 60)
                fit_sec = fit_time % 60
                print('Fitting completed in {} minutes {} seconds. Saving model to .pkl file \n'.format(fit_min,fit_sec))
                model_filename = model_folder + output_text + '_and_alpha' + str(av) + '.pkl'
                joblib.dump(nn_model, model_filename)

                print('Predicting...\n')
                y_pred_train = nn_model.predict(X)
                print('Validating...\n')
                y_pred_val = nn_model.predict(X_val)
                print('Getting scores\n')
                scr = nn_model.score(X,y)
                scr_val = nn_model.score(X_val,y_val)
                scrs.append(scr)
                scrs_val.append(scr_val)

                kc_train = np.mean((y_pred_persistence - y_pred_train) **2) #our persistence score
                kc_val = np.mean((y_pred_persistence_val - y_pred_val) **2)
                kc_train_scores.append(kc_train)
                kc_validation_scores.append(kc_val)


                k1val = np.mean((y_pred_val - y_val) **2) #our "custom" score for validation
                k1train = np.mean((y_pred_train - y) **2) #our "custom" score for training
                k1_train_scores.append(k1train)
                k1_validation_scores.append(k1val)


                k1_kc_train = k1train / kc_train
                k1_kc_val = k1val / kc_val
                k1_kc_train_scores.append(k1_kc_train)
                k1_kc_validation_scores.append(k1_kc_val)



            print('Saving figures and .csv file\n')
            #SAVING FIGURES FOR FIRST SCORE:
            plt.figure()
            plt.semilogx(alpha_values,scrs,label='train')
            plt.semilogx(alpha_values,scrs_val,label='validation')
            plt.legend(loc='best', fancybox=True, framealpha=0.5)
            plt.title('MLPRegressor score. Alpha dependence for feature values {} and {} of the data. Horizon prediction: {} . {} hidden layers with {} neurons'.format(stations,prcnt,hp,len_hls,hls_neurons_str))
            plt.savefig(graphs_folder + output_text + '.png',bbox_inches = 'tight')
            plt.close()

            #SAVING FIGURES FOR CUSTOM SCORES AND COMPARATIVES
            plt.figure()
            plt.semilogx(alpha_values,k1_train_scores,label='k1 custom train score')
            plt.semilogx(alpha_values,k1_validation_scores,label='k1 custom validation score')
            plt.semilogx(alpha_values,kc_train_scores,label='kc train persistence model score')
            plt.semilogx(alpha_values,kc_validation_scores,label='kc validation persistence model score')
            plt.legend(loc='best', fancybox=True, framealpha=0.5)
            plt.title('Custom scores. Alpha dependence for feature values {} and {} of the data. Horizon prediction: {} . {} hidden layers with {} neurons'.format(stations,prcnt,hp,len_hls,hls_neurons_str))
            plt.savefig(graphs_folder + output_text + '_custom_scores.png',bbox_inches='tight')
            plt.close()

            #SAVING FIGURES FOR COMPARATIVE OF SCORES K1/KC

            plt.figure()
            plt.semilogx(alpha_values,k1_kc_train_scores,label='k1/kc train score')
            plt.semilogx(alpha_values,k1_kc_validation_scores,label='k1/kc validation score')

            plt.legend(loc='best', fancybox=True, framealpha=0.5)
            plt.title('Custom scores ratio. Alpha dependence for feature values {} and {} of the data. Horizon prediction: {} . {} hidden layers with {} neurons'.format(stations,prcnt,hp,len_hls,hls_neurons_str))
            plt.savefig(graphs_folder + output_text + '_custom_scores_ratio.png',bbox_inches='tight')
            plt.close()

            #SAVING DATA AS .CSV
            alphas = pd.DataFrame(alpha_values)
            scores = pd.DataFrame(scrs)
            scores_validation = pd.DataFrame(scrs_val)
            scores_k1_validation = pd.DataFrame(k1_validation_scores)
            scores_k1_train = pd.DataFrame(k1_train_scores)
            scores_kc_train = pd.DataFrame(kc_train_scores)
            scores_kc_validation = pd.DataFrame(kc_validation_scores)
            scores_k1_kc_validation = pd.DataFrame(k1_kc_validation_scores)
            scores_k1_kc_train = pd.DataFrame(k1_kc_train_scores)
            df_alphascores = pd.concat([alphas,scores,scores_validation,scores_k1_train,scores_k1_validation,scores_kc_train,scores_kc_validation,scores_k1_kc_train,scores_k1_kc_validation],axis=1,ignore_index=True)

            df_alphascores.columns = ['alpha_values','scores_train_sklearn','scores_validation_sklearn','k1_score_train','k1_score_validation','kc_score_persistence_train','kc_score_persistence_validation','SCORE_k1/kc_train','SCORE_k1/kc_validation']
            df_alphascores.to_csv(csvs_folder + output_text + '.csv',header=True,index=False)

            print('Figures and .csv generated!\n')
