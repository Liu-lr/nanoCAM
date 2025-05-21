# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 17:13:35 2023

@author: Jiayong Zhong

Fill NaN in the deeptools heatmap matrix
"""
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from joblib import Parallel, delayed
import gzip
import json
import sys, os

def fill_missing_values(data):
    # 使用 KNN 算法填补缺失值
    #filled_data = KNN(k=3).fit_transform(data)
    imputer = KNNImputer(n_neighbors=10)
    filled_data = imputer.fit_transform(data)
    return pd.DataFrame(filled_data)

def parallel_run(rawdata, threads, func):
    """利用 Parallel 和 delayed 函数实现并行运算"""
    Ns = int( len(rawdata)/threads ) + 1
    data_dict = {}
    Ps = list( range(0, len(rawdata), Ns) )
    Ps.append( len(rawdata)  )
    for n in range(0, len(Ps)-1 )  :
        start, end = Ps[n], Ps[n+1]
        data_dict[n] = rawdata[start:end, :]
    results = Parallel(n_jobs=-1)(delayed(func)(group) for name, group in data_dict.items() )
    return pd.concat(results)


matrixfile = sys.argv[1]
# Load Matrix
fID = gzip.open(matrixfile, "rt")
headline = fID.readline()
headdict = json.loads(headline[1:])
fID.close()
## Matrix
matrixdf = pd.read_csv(matrixfile, header=None, index_col=None, skiprows=1, sep="\t")
## Fill matrix NaN
threads = int( len(matrixdf) / 200 )  # 200 rows each running thread
sample_labels = headdict['sample_labels']
IDlist, minlist, maxlist = [], [], [] ## Export min and max
for n in range(0, len(sample_labels ) ):
    idx_s, idx_e = headdict['sample_boundaries'][n]+6, headdict['sample_boundaries'][n+1]+6
    print(sample_labels[n], idx_s, idx_e-1)
    cols =  list(range(idx_s, idx_e) )
    rawmat = matrixdf.loc[:, cols].values
    #fillmat = fill_missing_values(rawmat)
    fillmat = parallel_run(rawmat, threads, fill_missing_values )
    matrixdf.loc[:, cols] =  fillmat.values
    ## min and max
    IDlist.append( sample_labels[n] )
    minlist.append( matrixdf.loc[:, cols].mean().min() )
    maxlist.append( matrixdf.loc[:, cols].mean().max() )
print("Sample min and max:")
print("SID:", IDlist)
print("min:", [round(n, 3) for n in minlist])
print("max:", [round(n, 3) for n in maxlist])

matrixdf = matrixdf.fillna(0)
# Export
Exportfile = matrixfile.replace(".mat.gz",".fillna.mat")
fID = open(Exportfile, "w")
fID.writelines(headline)
fID.close()
# Export fillnamat
matrixdf.to_csv(Exportfile, sep="\t", header=False, index=False, mode="a")
os.system( "gzip -f %s"%(Exportfile) )
