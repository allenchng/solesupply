import json
import csv
from pandas.io.json import json_normalize # package for flattening json in pandas df
import os
import pandas as pd

def ConvertJson(file):

    """Converts json list of transactions to long dataframe.

    Extracts sale transacations within a single json file. Each json file
    contains all transactions for a specific sneaker model. Converts
    the nested json structure into long datframe structure. 

    Args:
        file: File in json format

    Returns:
        A dataframe with the following columns:
            sku: Unique identification number on stockx website
            localAmount: Price shoe was sold
            createdAt: Date and time shoe was sold
            localCurrency: Default to us dollars (USD)
            shoeSize: Size of the shoe sold
    """

    base = file.split('/')[-1]
    sku = base.split('.')[0]
    
    with open(file) as f:
        d = json.load(f)
    
    df = json_normalize(d['ProductActivity'])
    df['sku'] = sku
    select_df = df.loc[:, ('sku', 'localAmount', 'createdAt', 'localCurrency', 'shoeSize')]
    
    return(select_df)

def ConcatJson(input_dir):

    """ Reads in a list of json files in a directory, extracts
    sales transactions from each json file, then concatenates
    transaction data to a dataframe.

    Args:
        input_dir: Directory housing json files

    Returns:
        A dataframe with the following columns:
            sku: Unique identification number on stockx website
            localAmount: Price shoe was sold
            createdAt: Date and time shoe was sold
            LocalCurrency: Default to us dollars (USD)
            shoeSize: Size of the shoe sold
    """

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