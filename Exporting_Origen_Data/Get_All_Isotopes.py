#! /usr/bin/env python2.7.5
#Author: Colin Gerber

import csv
import os
import pandas as pd


def convert_to_csv(out_file_list):
    '''takes an .out file with specific type of output in it and takes a prespecified section
    of it to output to a csv file.'''

    # creates a list to iterate through the 50 files
    df_tot = pd.DataFrame()
    for f in out_file_list:
        if 'compiled' in f:
            continue
        else:
            df_infile = pd.read_csv(f, index_col=0, header=None)
            df_infile = df_infile.T

            if len(df_tot) == 0:
                df_tot = df_infile
            else:
                df_tot = df_tot.append(df_infile)
    df_tot.to_csv('All_isotopes.csv')


def get_csv(directory):
    tot_dir_list = os.listdir(directory)
    return [f for f in tot_dir_list if 'export.csv' in f]


def main():
    while (True):
        directory = raw_input('Enter the path of the directory your files are in: ')
        try:
            os.chdir(directory)

            #get a list of .out files
            out_file_list = get_csv(directory)

            convert_to_csv(out_file_list)
            break
        except Exception as e:
            print (e)
            print ('That path does not work, please try entering it again.')


# code execution begins and invokes main()
if __name__ == '__main__':
    main()
