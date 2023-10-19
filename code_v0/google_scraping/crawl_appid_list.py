from bs4 import BeautifulSoup
import requests, json, lxml, re
import time
import sys, getopt
import google_play_scraper
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import codecs
import os
import pandas as pd
from subprocess import Popen, PIPE
import json

def progress_bar(current, total, name, current_alt, bar_length = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))

    print(name+': [%s%s] %d/%d (%d apps) %d %%' % (arrow, spaces, current, total, current_alt, percent), end='\r')
    
def tokenize_description(text, stop_words):
    word_tokens = word_tokenize(text)
    word_tokens = [w.lower() for w in word_tokens]
    filtered_text = [w for w in word_tokens if not w.lower() in stop_words]
    filtered_text = [w for w in filtered_text if len(w)>1]
    filtered_text = [w for w in filtered_text if not any([y in w for y in ["href", "url", "http", "\\", "/"]])]
    return filtered_text

def app_details_nodejs(app_id):
    process = Popen(['node', 'app_details.js', app_id], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = None
    return result

def developer_apps_nodejs(dev_id):
    process = Popen(['node', 'developer_apps.js', "\""+dev_id+"\""], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = None
    return result

def similar_apps_nodejs(app_id):
    process = Popen(['node', 'similar_apps.js', app_id], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = None
    return result

def main_gatherer(filename1, filename2):

    allowed_genres = ["Medical", "Health & Fitness"]
    batch_size = 1000
    batch = 1
    developers_considered = []
    app_cache = []
    app_cache_ids = []
    app_ids = []
    app_sizes = []
    app_android = []
    app_installs_2021 = []
    for filename in [filename1, filename2]:
        with open(filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip().split('\t')
                app_ids.append(line[0])
                app_sizes.append(line[5])
                if len(line)>6:
                    app_android.append(line[6])
                else:
                    app_android.append('NA')
                app_installs_2021.append(line[4])
    
    apps_data = []
    apps_queried = []
    for i in range(len(app_ids)):
        progress_bar(i, len(app_ids), "Extracting details", len(apps_data), bar_length = 20)
        app_id = app_ids[i]
        if app_id in app_cache_ids:
            result = app_cache[app_cache_ids.index(app_id)]
            del app_cache[app_cache_ids.index(app_id)]
            del app_cache_ids[app_cache_ids.index(app_id)]
        else:
            result = app_details_nodejs(app_id)
        if result is None:
            continue
        if not result['available']:
            continue
        
        apps_data.append({
            "id": result['appId'],
            "title": result['title'],
            "summary": result['summary'] if 'summary' in result.keys() else 'NA',
            "description": result['description'],
            "released": result['released'] if 'released' in result.keys() else 'NA',
            "installs_2021": app_installs_2021[i],
            "installs_2022": result['maxInstalls'],
            "size": app_sizes[i],
            "android_2021": app_android[i],
            "android_2022": result['androidVersion'],
            "score": result['score'] if 'score' in result.keys() else 'NA',
            "ratings": result['ratings'] if 'ratings' in result.keys() else 'NA',
            "histogram": result['histogram'] if 'histogram' in result.keys() else 'NA',
            "reviews": result['reviews'] if 'reviews' in result.keys() else 'NA',
            "iap": result['offersIAP'],
            "category": result['genre'],
            "developer": result['developer']
            })
        
        apps_queried.append(result['appId'])
        if result['developer'] not in developers_considered:
            developers_considered.append(result['developer'])
            dev_apps = developer_apps_nodejs(result['developer'])
            if dev_apps is not None:
                for app in dev_apps:
                    if app['appId'] not in apps_queried and app['appId'] not in app_cache_ids:
                        if app['genre'] not in allowed_genres or not app['available']:
                            continue
                        app_cache.append(app)
                        app_cache_ids.append(app['appId'])
        
        similar_apps = similar_apps_nodejs(result['appId'])
        if similar_apps is not None:
            for app in similar_apps:
                if app['appId'] not in apps_queried and app['appId'] not in app_cache_ids:
                    if app['genre'] not in allowed_genres or not app['available']:
                        continue
                    app_cache.append(app)
                    app_cache_ids.append(app['appId'])
                    
        if len(apps_data)>batch_size:
            print("\nPrinting batch "+str(batch)+" consisting of "+str(len(apps_data))+" apps ...\n")
            json_string = json.dumps(apps_data)
            with open('data/master_json/MedicalHealthFitness_batch'+str(batch)+'.json', 'w') as outfile:
                outfile.write(json_string)
            batch=batch+1
            apps_data = []
    
    if len(apps_data)>0:
        print("\nPrinting batch "+str(batch)+" consisting of "+str(len(apps_data))+" apps ...\n")
        json_string = json.dumps(apps_data)
        with open('data/master_json/MedicalHealthFitness_batch'+str(batch)+'.json', 'w') as outfile:
            outfile.write(json_string)
        batch=batch+1
        apps_data = []
        
    for i in range(len(app_cache_ids)):
        result = app_cache[i]
        apps_data.append({
            "id": result['appId'],
            "title": result['title'],
            "summary": result['summary'] if 'summary' in result.keys() else 'NA',
            "description": result['description'],
            "released": result['released'] if 'released' in result.keys() else 'NA',
            "installs_2021": 'NA',
            "installs_2022": result['maxInstalls'],
            "size": 'NA',
            "android_2021": 'NA',
            "android_2022": result['androidVersion'],
            "score": result['score'] if 'score' in result.keys() else 'NA',
            "ratings": result['ratings'] if 'ratings' in result.keys() else 'NA',
            "histogram": result['histogram'] if 'histogram' in result.keys() else 'NA',
            "reviews": result['reviews'] if 'reviews' in result.keys() else 'NA',
            "iap": result['offersIAP'],
            "category": result['genre'],
            "developer": result['developer']
            })
        
    print("\nPrinting last batch consisting of "+str(len(apps_data))+ " new apps ...\n")
    json_string = json.dumps(apps_data)
    with open('data/master_json/MedicalHealthFitness_batch'+str(batch)+'.json', 'w') as outfile:
        outfile.write(json_string)
 
try:
    opts, args = getopt.getopt(sys.argv[1:],"hf:g:",["filename1=","filename2="])
except getopt.GetoptError:
    print('crawl_appid_list.py -f <filename1> -g <filename2>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('crawl_appid_list.py -f <filename1> -g <filename2>')
        sys.exit()
    elif opt in ("-f", "--filename1"):
        filename1 = arg
    elif opt in ("-g", "--filename1"):
        filename2 = arg

main_gatherer(filename1, filename2)
