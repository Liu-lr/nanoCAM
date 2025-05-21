#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd
import numpy as np
import itertools
from itertools import combinations
from pandas import Series
import time
from rich.progress import track
import sys
import os
import multiprocessing
pd.set_option('future.no_silent_downcasting', True)


# In[2]:


def LoadMatrixReader(filename, Chunksize, colnamelist,  sepstr="\t"):
    file_reader = pd.read_table(filename, sep=sepstr,
                                chunksize=Chunksize, iterator=True,
                                header=None, index_col=None, names = colnamelist, low_memory=False)
    return(file_reader)

def CompleteDF(df, dfhold, Chunksize):
    lastread = df.iloc[-1]["readID"]
    df = pd.concat([dfhold, df]) # concat dfhold and df
    # last read df
    P = df["readID"] == lastread
    dfhold = df.loc[P, :].copy()
    if len(df) >= Chunksize: # not the last iterally loading
        df = df.drop(df.loc[P].index.to_list() , axis=0)

    return(df, dfhold)

def PrintTime():
    now = datetime.datetime.now()
    otherStyleTime = now.strftime("%Y--%m--%d %H:%M:%S")
    print(otherStyleTime)


# In[3]:


def func(key, value):
    Dict_format = {"read_name":[], "strand1":[], "chrom1":[], "pos1":[], "frag1":[], 
                   "strand2":[], "chrom2":[], "pos2":[], "frag2":[], "mapq1":[], "mapq2":[]}
        
    
    # list1 = value["frag"].values
    # list2 = list(combinations(list1, 2))
    
    index = value.index
    index_list = list(combinations(index,2))
    index_list = [list(row) for row in index_list]
    
    tmp = []
    for i in index_list:
        
        Dict_format["read_name"].append(key)
        contact = value.loc[i]
        
        Dict_format["strand1"].append(contact.loc[i[0], "strand"])
        Dict_format["chrom1"].append(contact.loc[i[0], "chrom"])
        Dict_format["pos1"].append(contact.loc[i[0], "pos"])
        Dict_format["frag1"].append(contact.loc[i[0], "frag"])
    
        Dict_format["strand2"].append(contact.loc[i[1], "strand"])
        Dict_format["chrom2"].append(contact.loc[i[1], "chrom"])
        Dict_format["pos2"].append(contact.loc[i[1], "pos"])
        Dict_format["frag2"].append(contact.loc[i[1], "frag"])
    
        Dict_format["mapq1"].append(contact.loc[i[0], "mapq"])
        Dict_format["mapq2"].append(contact.loc[i[1], "mapq"])

    return pd.DataFrame(Dict_format)

def func_wrapper(args):
    """pass parameter"""
    return func(*args)


# In[4]:


def make_readid_dict(df):
    readID_dict = {}
    df['strand'] = df['strand'].replace("+", 0)
    df['strand'] = df['strand'].replace("-", -1)
    df['pos'] = (df['start'] + df['end']) / 2
    df["pos"] = df["pos"].astype(int)
    df_group = df.groupby(df.readID)
    for readID, gdf in df_group:
        readID_dict[readID] = gdf.reset_index(drop = True)

    return readID_dict


# In[ ]:


def main() :
    colnamelist = ["chrom", "start", "end", "readID", "mapq", "strand", "frag"]
    reader  =  LoadMatrixReader(bedfile_path, Chunksize, colnamelist,  sepstr="\t")
    CountDict = []
    df_hold = pd.DataFrame()
    for chunk in track(reader, description="Processing...", transient=True):
        chunk, df_hold = CompleteDF(chunk, df_hold, Chunksize)
        print("make dict done!")
        # 计算当前数据块中，每个readID的出现次数
        readcount_df = pd.DataFrame(chunk['readID'].value_counts())
        # 筛选出出现次数大于等于2的readID，并将其转换为列表
        tmp_list = list(readcount_df.loc[readcount_df['count'] >= 2].index)
        # 根据筛选出的readID列表，提取出对应的行
        chunk = chunk.loc[chunk['readID'].isin(tmp_list)]
        rid_dict = make_readid_dict(chunk)
        with multiprocessing.Pool(processes=thread) as pool:
            args_list = [(key, value) for key, value in rid_dict.items()]
            result = pool.map(func_wrapper, args_list)
        print("concat!")
        tmp = pd.concat(result)
        tmp = tmp.astype({"pos1":int, "frag1":int, "pos2":int, "frag2":int, "mapq1":int, "mapq2":int})
        tmp.to_csv(outfile_path, sep = "\t", index = 0, mode = 'a', header = 0)
        del tmp
        del rid_dict
        del result
        del tmp_list
        del readcount_df

# In[ ]:


if __name__=="__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py input_path out_path Chunksize Thread")
        sys.exit(1)
    print("need to sort the file first!")
    # 调用函数并指定目标文件夹路径
    # directory_path = "/data1/LLR/REPEAT_CHM13/nanoNOMe/gpc"
    bedfile_path = sys.argv[1]
    outfile_path = sys.argv[2]
    Chunksize = int(sys.argv[3])
    thread = int(sys.argv[4])
    if os.path.exists(outfile_path):
        print(f"{outfile_path} exist!")
        sys.exit(1)
    main()

