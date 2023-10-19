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

def progress_bar(current, total, name, bar_length = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))

    print(name+': [%s%s] %d/%d %d %%' % (arrow, spaces, current, total, percent), end='\r')
    
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

def get_apps_queried():
    apps_queried = []
    with open("data/master_json/temporary_bookkeeping/apps_queried.txt") as f:
        while True:
            line = f.readline()
            if not line:
                break
            apps_queried.append(line.strip())
            
    return apps_queried

def get_apps_unavailable():
    apps_unavailable = []
    with open("data/master_json/temporary_bookkeeping/apps_unavailable.txt") as f:
        while True:
            line = f.readline()
            if not line:
                break
            apps_unavailable.append(line.strip())
            
    return apps_unavailable

def update_apps_queried(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_queried.txt", "a") as f:
        f.write(app_id+"\n")
      
def update_apps_unavailable(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_unavailable.txt", "a") as f:
        f.write(app_id+"\n")
        
def update_state(i, tot, start):
    with open("data/master_json/temporary_bookkeeping/state"+str(start)+".txt", "w") as f:
        f.write(str(i)+"\t"+str(tot)+"\n")

def write_app(result, info_2021):
    app_data = {
        "id": result['appId'],
        "title": result['title'],
        "summary": result['summary'] if 'summary' in result.keys() else 'NA',
        "description": result['description'],
        "released": result['released'] if 'released' in result.keys() else 'NA',
        "installs_2021": info_2021[0],
        "installs_2022": result['maxInstalls'],
        "size": info_2021[1],
        "android_2021": info_2021[2],
        "android_2022": result['androidVersion'],
        "score": result['score'] if 'score' in result.keys() else 'NA',
        "ratings": result['ratings'] if 'ratings' in result.keys() else 'NA',
        "histogram": result['histogram'] if 'histogram' in result.keys() else 'NA',
        "reviews": result['reviews'] if 'reviews' in result.keys() else 'NA',
        "iap": result['offersIAP'],
        "category": result['genre'],
        "developer": result['developer']
        }
        
    json_string = json.dumps(app_data)
    with open('data/master_json/app_individual_jsons/'+result['appId']+'.json', 'w') as outfile:
        outfile.write(json_string)
          
def main_gatherer(filename1, filename2, start):

    apps_queried = get_apps_queried()
    allowed_genres = ["Medical", "Health & Fitness"]
    developers_considered = []
    app_cache = []
    app_cache_ids = []
    app_ids = []
    app_sizes = []
    app_android = []
    app_installs_2021 = []
    tot_apps = 0
    for filename in [filename1, filename2]:
        with open(filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip().split('\t')
                tot_apps = tot_apps + 1
                if line[0] in apps_queried:
                    continue
                app_ids.append(line[0])
                app_sizes.append(line[5])
                if len(line)>6:
                    app_android.append(line[6])
                else:
                    app_android.append('NA')
                app_installs_2021.append(line[4])
    
    for i in range(len(app_ids)):
        if i<start:
            continue
        update_state(i, len(app_ids), start)
        app_id = app_ids[i]
        apps_unavailable = get_apps_unavailable()
        if app_id in apps_unavailable:
            continue
        apps_queried = get_apps_queried()
        progress_bar(len(apps_queried), tot_apps, "Extracting details", bar_length = 20)
        if app_id in apps_queried:
            continue
        if app_id in app_cache_ids:
            result = app_cache[app_cache_ids.index(app_id)]
            del app_cache[app_cache_ids.index(app_id)]
            del app_cache_ids[app_cache_ids.index(app_id)]
        else:
            result = app_details_nodejs(app_id)
        if result is None:
            update_apps_unavailable(app_id)
            continue
        if not result['available']:
            update_apps_unavailable(app_id)
            continue
        update_apps_queried(app_id)
        write_app(result, [app_installs_2021[i], app_sizes[i], app_android[i]])
                
        if result['developer'] not in developers_considered:
            developers_considered.append(result['developer'])
            dev_apps = developer_apps_nodejs(result['developer'])
            if dev_apps is not None:
                for app in dev_apps:
                    apps_unavailable = get_apps_unavailable()
                    if app['appId'] in apps_unavailable:
                        continue
                    if app['genre'] not in allowed_genres or not app['available']:
                        update_apps_unavailable(app_id)
                        continue
                    apps_queried = get_apps_queried()
                    if app['appId'] not in apps_queried:    
                        update_apps_queried(app['appId'])
                        if app['appId'] in app_ids:
                            I = app_ids.index(app['appId'])
                            write_app(app, [app_installs_2021[I], app_sizes[I], app_android[I]])
                        else:
                            write_app(app, ['NA', 'NA', 'NA'])
        
        similar_apps = similar_apps_nodejs(result['appId'])
        if similar_apps is not None:
            for app in similar_apps:
                apps_unavailable = get_apps_unavailable()
                if app['appId'] in apps_unavailable:
                    continue
                if app['genre'] not in allowed_genres or not app['available']:
                    update_apps_unavailable(app_id)
                    continue
                apps_queried = get_apps_queried()
                if app['appId'] not in apps_queried:    
                    update_apps_queried(app['appId'])
                    if app['appId'] in app_ids:
                        I = app_ids.index(app['appId'])
                        write_app(app, [app_installs_2021[I], app_sizes[I], app_android[I]])
                    else:
                        write_app(app, ['NA', 'NA', 'NA'])
                    
 
try:
    opts, args = getopt.getopt(sys.argv[1:],"hf:g:s:",["filename1=","filename2=", "start="])
except getopt.GetoptError:
    print('crawl_appid_list_parallel.py -f <filename1> -g <filename2> -s <start')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('crawl_appid_list_parallel.py -f <filename1> -g <filename2> -s <start>')
        sys.exit()
    elif opt in ("-f", "--filename1"):
        filename1 = arg
    elif opt in ("-g", "--filename1"):
        filename2 = arg
    elif opt in ("-s", "--start"):
        start = 6000*int(arg)

main_gatherer(filename1, filename2, start)
