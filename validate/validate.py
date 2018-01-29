import pandas as pd
import os

input_folder = 'input'
input_files = os.listdir('input')
nfiles = len(input_files)

t_columns = ['s', 'y', 'doy', 'hst']
sta_columns = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11',
             'dh9', 'dh2', 'dh1', 'dh1tilt', 'ap6',
             'ap6tilt', 'ap1', 'ap3', 'ap5', 'ap4',
             'ap7', 'dh6', 'dh7', 'dh8']

# Stations to consider
stations = ['dh3', 'dh4', 'dh5', 'dh10', 'dh11', 'dh9', 'dh2', 'dh1',
            'ap6', 'ap1', 'ap3', 'ap5', 'ap4', 'ap7', 'dh6', 'dh7', 'dh8']

# Only consider data between 07:30 and 17:30 (HST)
initial_hour = 730
final_hour = 1729

n = 0
m = 0

for input_file in input_files:
    valid = True
    input_path = input_folder + '/' + input_file
    print('[{}/{}] Reading {}...'.format(input_files.index(input_file)+1, nfiles, input_path), end=' ')

    df = pd.read_csv(input_path, header=None, names=t_columns+sta_columns)

    # Take daylight data
    df = df[(df.hst >= initial_hour) & (df.hst <= final_hour)]

    for station in stations:
        if False in (df[stations] > 0.0).values:
            n += 1
            valid = False
            print('Negative values were found... We will skip this day')
        else:
            for i in range(len(df.s) - 1):
                if (df.s.iloc[i+1] - df.s.iloc[i]) not in (1, -59):
                    m += 1
                    valid = False
                    print('Some seconds are missing... We will skip this day')
                    break

        if valid:
            print('Data seem valid!')

print('\nTotal files: ' + str(nfiles))
print('Ivalid files: ' + str(n+m))
print('\tFiles with negative values: ' + str(n))
print('\tFiles with missing seconds: ' + str(m))
print('Valid files: ' + str(nfiles-n))
