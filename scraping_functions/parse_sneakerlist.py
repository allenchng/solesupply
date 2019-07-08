import re
import pandas as pd
import os

def parse_stockx(file):
    with open(file,'r') as f:
        name = [line for line in f if 'name' in line]
    with open(file,'r') as f:
        releaseDate = [line for line in f if 'releaseDate' in line]
    with open(file,'r') as f:
        brand = [line for line in f if 'brand' in line]
    with open(file,'r') as f:
        model = [line for line in f if 'model' in line]
    with open(file,'r') as f:
        sku = [line for line in f if 'sku' in line]
    with open(file,'r') as f:
        color = [line for line in f if '"color" : ' in line]
    
    df = pd.DataFrame({'name':name,
            'releaseDate':releaseDate,
            'brand':brand,
            'model':model,
            'sku':sku,
            'color':color})
    return(df)

def format_data(df):
    df = df.applymap(lambda x: x.replace('"', ''))
    for i in df.columns:
        df[str(i)] = df[str(i)].str.split('\:').str[-1].str.strip()
        df[str(i)] = df[str(i)].str.replace(',', '')
    
    # creat new column for url scraping
    front = 'https://stockx.com/api/products/'
    end = '/activity?state=480&currency=USD&limit=20000&page=1&sort=createdAt&order=DESC'
    
    df['api_url'] = front + df['sku'] + end
    return(df)