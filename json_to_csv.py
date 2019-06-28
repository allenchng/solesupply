import json
import csv
from pandas.io.json import json_normalize #package for flattening json in pandas df
import os
import pandas as pd

def ConvertJson(file):
    base = file.split('/')[-1]
    sku = base.split('.')[0]
    
    with open(file) as f:
        d = json.load(f)
    
    df = json_normalize(d['ProductActivity'])
    df['sku'] = sku
    select_df = df.loc[:, ('sku', 'localAmount', 'createdAt', 'localCurrency', 'shoeSize')]
    
    return(select_df)

def ConcatJson(input_dir):
    json_list = [f for f in os.listdir(input_dir) if not f.startswith('.')]
    
    d = {'sku':[],
     'localAmount':[],
     'createdAt':[],
     'localCurrency':[],
     'shoeSize':[]}

    df = pd.DataFrame(d)
    
    for item in json_list:
        file_str = input_dir + ''.join(item)
        tmp_df = ConvertJson(file_str)
    
        df = pd.concat([df, tmp_df])
    
    return(df)