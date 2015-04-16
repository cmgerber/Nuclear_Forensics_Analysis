#!/usr/bin/python
# -*- coding: utf-8 -*-
#author: Colin Gerber

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import Nuclear_Reactor_Sample_Regression_Match_PCA as PCA_Regression

def get_PCA_data(unknown_sample):
    #import data
    df = pd.read_excel('All_Isotopes_Generated.xlsx', 'Sheet1')

    needed_isotopes = ['Reactor', 'Enrichment', 'u234', 'u235', 'u236', 'u238',
                       'pu238', 'pu239', 'pu240', 'pu241', 'pu242']

    df = df[needed_isotopes]
    df = df.append(unknown_sample)

    # split data table into data X and class labels y
    x = df.ix[:,2:].values
    reactor = df.ix[:,0].values
    enrichment = df.ix[:,1].values

    x_std = StandardScaler().fit_transform(x)
    #x_std = x

    pca_model = PCA(n_components=3)
    result = pca_model.fit_transform(x_std)

    df_result = pd.DataFrame(result, columns=['PC1', 'PC2', 'PC3'])
    df_result['reactor'] = reactor
    df_result['enrichment'] = enrichment
    df_result = df_result[df_result.columns[-2:].append(df_result.columns[:-2])]
    return df_result

def main():
    #prep unknown sample
    df = pd.read_csv('marakova-table-7-rbmk-spent-fuel-wo-uncertainty.csv')
    df = df.apply(lambda x: x*1000)
    df['Reactor'] = ['unknown']* len(df)
    df['Enrichment'] = [1]* len(df)
    needed_isotopes = ['Reactor', 'Enrichment', 'u234', 'u235', 'u236', 'u238',
                       'pu238', 'pu239', 'pu240', 'pu241', 'pu242']
    df = df[needed_isotopes]

    df_test_data = pd.DataFrame()

    for ix, row in df.iterrows():
        df_result = get_PCA_data(row)
        df_test_data = df_test_data.append(df_result.iloc[-1,:])
    PCA_Regression.data_analysis(df_result, df_test_data)



if __name__ == '__main__':
    main()
