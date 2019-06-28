import requests
import json
import random
import csv
import time
import os

def ScrapeStockX(url):
    url_str = ''.join(url)
    sku = url_str.split('/')[-2]
    data = requests.get(url_str)
    json_dict = data.json()
    
    out_dir = './stockx_jsons/'
    out_name = out_dir + sku + '.json'

    with open(out_name, 'w+') as f:
        json.dump(json_dict, f, sort_keys=True, indent=4)
    print(str(sku)+ ' has been successfully scraped!')

def ScrapeBrands(input_dir):
    file_list = [f for f in os.listdir(input_dir) if not f.startswith('.')]
    
    for file in file_list:
        file_str = input_dir + ''.join(file)

        with open(file_str, 'r') as f:
            reader = csv.reader(f)
            url_list = list(reader)

        for i in url_list:
            ScrapeStockX(i)
            time.sleep(random.randint(15, 45))
        print(file_str + ' has completed scraping!')

