# %%
# imports and functions

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
from collections import Counter
import random

def progress_bar(current, total, name, bar_length = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * bar_length - 1) + '>'
    spaces  = ' ' * (bar_length - len(arrow))

    print(name+': [%s%s] %d/%d %d %%' % (arrow, spaces, current, total, percent), end='\r')
    
def search_store_nodejs(search_term, n):
    process = Popen(['node', 'search_app_store.js', search_term, str(n)], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = None
    return result

def app_details_nodejs(app_id):
    process = Popen(['node', 'app_details.js', app_id], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = stdout
    return result

def developer_apps_nodejs(dev_id):
    process = Popen(['node', 'developer_apps.js', dev_id], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = stdout
    return result

def similar_apps_nodejs(app_id):
    process = Popen(['node', 'similar_apps.js', app_id], stdout=PIPE)
    stdout = process.communicate()[0]
    try:
        result = json.loads(stdout)
    except:
        result = stdout
    return result

def get_apps_queried():
    apps_queried = []
    if os.path.exists("data/master_json/temporary_bookkeeping/apps_queried.txt"):
        with open("data/master_json/temporary_bookkeeping/apps_queried.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                apps_queried.append(line.strip())
            
    return apps_queried

def get_apps_to_query():
    apps_to_query = []
    if os.path.exists("data/master_json/temporary_bookkeeping/apps_to_query.txt"):
        with open("data/master_json/temporary_bookkeeping/apps_to_query.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                apps_to_query.append(line.strip())
            
    return apps_to_query

def get_apps_queried_for_developer():
    apps_queried_for_developer = []
    if os.path.exists("data/master_json/temporary_bookkeeping/apps_queried_for_developer.txt"):
        with open("data/master_json/temporary_bookkeeping/apps_queried_for_developer.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                apps_queried_for_developer.append(line.strip())
            
    return apps_queried_for_developer

def get_apps_queried_for_similar():
    apps_queried_for_similar = []
    if os.path.exists("data/master_json/temporary_bookkeeping/apps_queried_for_similar.txt"):
        with open("data/master_json/temporary_bookkeeping/apps_queried_for_similar.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                apps_queried_for_similar.append(line.strip())
            
    return apps_queried_for_similar

def get_non_genre_apps():
    non_genre_apps = []
    if os.path.exists("data/master_json/temporary_bookkeeping/nongenre_apps.txt"):
        with open("data/master_json/temporary_bookkeeping/nongenre_apps.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                non_genre_apps.append(line.strip())
        
    return non_genre_apps

def get_developers_queried():
    developers_queried = []
    if os.path.exists("data/master_json/temporary_bookkeeping/developers_queried.txt"):
        with open("data/master_json/temporary_bookkeeping/developers_queried.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                developers_queried.append(line.strip())
            
    return developers_queried

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
      
def update_developers_queried(dev_id):
    with open("data/master_json/temporary_bookkeeping/developers_queried.txt", "a") as f:
        f.write(dev_id+"\n")
        
def update_apps_to_query(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_to_query.txt", "a") as f:
        f.write(app_id+"\n")
        
def update_apps_queried_for_similar(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_queried_for_similar.txt", "a") as f:
        f.write(app_id+"\n")
    
def update_apps_queried_for_developer(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_queried_for_developer.txt", "a") as f:
        f.write(app_id+"\n")
            
def update_nongenre_apps(app_id):
    with open("data/master_json/temporary_bookkeeping/nongenre_apps.txt", "a") as f:
        f.write(app_id+"\n")
        
def update_apps_unavailable(app_id):
    with open("data/master_json/temporary_bookkeeping/apps_unavailable.txt", "a") as f:
        f.write(app_id+"\n")
        
def update_state(i, tot, start):
    with open("data/master_json/temporary_bookkeeping/state"+str(start)+".txt", "w") as f:
        f.write(str(i)+"\t"+str(tot)+"\n")
        
os.makedirs(f'data/master_json/temporary_bookkeeping', exist_ok=True)
os.makedirs(f'data/master_json/app_individual_jsons', exist_ok=True)


# %%
# Write app function

def write_app(result, info_2021):
    app_data = {
        "id": result['appId'],
        "title": result['title'],
        "description": result['description'],
        "released": result['released'] if 'released' in result.keys() else 'NA',
        "updated": result['updated'] if 'updated' in result.keys() else 'NA',
        "required_os": result['requiredOsVersion'],
        "required_os_2021": info_2021[0],
        "size": result['size'],
        "size_2021": info_2021[1],
        "score": result['score'] if 'score' in result.keys() else 'NA',
        "score_2021": info_2021[2],
        # "ratings": result['ratings'] if 'ratings' in result.keys() else 'NA',
        # "histogram": result['histogram'] if 'histogram' in result.keys() else 'NA',
        "reviews": result['reviews'] if 'reviews' in result.keys() else 'NA',
        "reviews_2021": info_2021[3],
        "price": result['price'],
        "currency": result['currency'],
        "price_2021": info_2021[4],
        "currency_2021": info_2021[5],
        "category": result['primaryGenre'],
        "genres": ", ".join(result['genres']),
        "languages": ", ".join(result["languages"]),
        "developer": result['developerId'],
        "url": result["url"]
        }
        
    json_string = json.dumps(app_data)
    with open('data/master_json/app_individual_jsons/'+result['appId']+'.json', 'w') as outfile:
        outfile.write(json_string)

# %%
df_apps = pd.read_csv("appleAppData.csv", index_col=False)
df_mhf = df_apps.loc[(df_apps["Primary_Genre"]=="Medical") | (df_apps["Primary_Genre"]=="Health & Fitness"),:]
apps_2021 = df_mhf["App_Id"].to_list()

try:
    opts, args = getopt.getopt(sys.argv[1:],"hs:",["start="])
except getopt.GetoptError:
    print('scrape_appstore.py -s <start>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print('scrape_appstore.py -s <start>')
        sys.exit()
    elif opt in ("-s", "--start"):
        start = int(arg)
        
# %%
allowed_genres = ["Medical", "Health & Fitness"]

dev_id = "0"
apps_queried_for_developer = get_apps_queried_for_developer()
apps_queried_for_similar = get_apps_queried_for_similar()
developers_queried = get_developers_queried()
non_genre_apps = get_non_genre_apps()
apps_to_query = get_apps_to_query()
apps_queried = get_apps_queried()
n_done = len(set(apps_to_query).intersection(set(apps_queried)))
sampled = []

while True:
    # i += 1
    i = random.sample(range(len(apps_to_query)), 1)[0]
    
    if i in sampled:
        continue
    else:
        sampled.append(i)
        
    # Update status of crawling
    if i%5==0:
        apps_queried_for_developer = get_apps_queried_for_developer()
        apps_queried_for_similar = get_apps_queried_for_similar()
        developers_queried = get_developers_queried()
        non_genre_apps = get_non_genre_apps()
        apps_to_query = get_apps_to_query()
        apps_queried = get_apps_queried()
        n_done = len(set(apps_to_query).intersection(set(apps_queried)))
        
    app_id = apps_to_query[i]
    tot_apps = len(apps_to_query)
    
    # Step 1: Check if app has been queried already and skip if it has been
    update_state(i, tot_apps, start)
    
    progress_bar(n_done, tot_apps, "Extracting details", bar_length = 20)
    
    # Step 2: If app not queried yet, query for app details and mark app as currently queried
    developer_query = False
    if app_id in apps_queried and app_id not in apps_queried_for_developer:
        if os.path.exists(f"data/master_json/app_individual_jsons/{app_id}.json"):
            with open(f"data/master_json/app_individual_jsons/{app_id}.json", "r") as f:
                result = json.load(f)
            dev_id = str(result["developer"])
            developer_query = True
    elif app_id in apps_queried:
        if os.path.exists(f"data/master_json/app_individual_jsons/{app_id}.json"):
            with open(f"data/master_json/app_individual_jsons/{app_id}.json", "r") as f:
                result = json.load(f)
            dev_id = str(result["developer"])
            developer_query = True
    else:
        if not os.path.exists(f"data/master_json/app_individual_jsons/{app_id}.json"):
            result = app_details_nodejs(app_id)
            if "code" in result or "response" in result:
                # network gone or timeout
                timeout = 1
                update_state("app details timeout/network error", tot_apps, start)
                print(f"\nBreaking {start}\n")
                break
            elif len(result)==0:
                update_apps_queried(app_id)
                apps_queried.append(app_id)
                continue
            if app_id in apps_2021:
                info_2021 = df_mhf.loc[df_mhf["App_Id"]==app_id, ["Required_IOS_Version", "Size_Bytes", "Average_User_Rating", "Reviews", "Price", "Currency"]].iloc[0,:].to_list()
                info_2021 = [str(x) for x in info_2021]
                write_app(result, info_2021)
            else:
                write_app(result, ['NA']*6)
                
            dev_id = str(result["developerId"])
        else:
            with open(f"data/master_json/app_individual_jsons/{app_id}.json", "r") as f:
                result = json.load(f)
            dev_id = str(result["developer"])
            
        update_apps_queried(app_id)
        apps_queried.append(app_id)    
        developer_query = True
        
    time.sleep(0.2)
    
    # Step 3: Query similar apps for this app
    if app_id not in apps_queried_for_similar:
        similar_apps = similar_apps_nodejs(app_id)
        if "code" in similar_apps or "response" in similar_apps:
            # network gone or timeout
            timeout = 1
            update_state("similar timeout/network error", tot_apps, start)
            # print(f"\nBreaking {start}\n")
            # break
            
        elif len(similar_apps)>0:
            apps_queried_for_similar.append(app_id)
            update_apps_queried_for_similar(app_id)
            if similar_apps is not None:
                for app in similar_apps:
                    if len(set(app['genres']).intersection(set(allowed_genres)))==0 and app['appId'] not in non_genre_apps:
                        non_genre_apps.append(app['appId'])
                        update_nongenre_apps(app['appId'])
                    # apps_queried = get_apps_queried()
                    if app['appId'] not in apps_queried:    
                        if len(set(app['genres']).intersection(set(allowed_genres)))==0:
                            continue
                        
                        # If the similar app is Medical, Health & Fitness, write it
                        if not os.path.exists(f"data/master_json/app_individual_jsons/{app['appId']}.json"):
                            if app['appId'] in apps_2021:
                                info_2021 = df_mhf.loc[df_mhf["App_Id"]==app['appId'], ["Required_IOS_Version", "Size_Bytes", "Average_User_Rating", "Reviews", "Price", "Currency"]].iloc[0,:].to_list()
                                info_2021 = [str(x) for x in info_2021]
                                write_app(app, info_2021)
                            else:
                                write_app(app, ['NA']*6)
                                
                        update_apps_queried(app['appId'])
                        update_apps_to_query(app['appId'])
                        
    # Step 4: Get developer and check if developer has been queried, if not write and add developer to list
    if dev_id not in developers_queried and developer_query:
        dev_apps = developer_apps_nodejs(dev_id)
        if "code" in dev_apps or "response" in dev_apps:
            # network gone or timeout
            timeout = 1
            update_state("developer timeout/network error", tot_apps, start)
            # print(f"\nBreaking {start}\n")
            # break
        elif len(dev_apps)>0:
            developers_queried.append(dev_id)
            update_developers_queried(dev_id)
            apps_queried_for_developer.append(app_id)
            update_apps_queried_for_developer(app_id)
            if dev_apps is not None:
                for app in dev_apps:
                    if len(set(app['genres']).intersection(set(allowed_genres)))==0 and app['appId'] not in non_genre_apps:
                        non_genre_apps.append(app['appId'])
                        update_nongenre_apps(app['appId'])
                    # apps_queried = get_apps_queried()
                    if app['appId'] not in apps_queried:
                        if len(set(app['genres']).intersection(set(allowed_genres)))==0:
                            continue
                        
                        # If the developer app is Medical, Health & Fitness, write it
                        if not os.path.exists(f"data/master_json/app_individual_jsons/{app['appId']}.json"):
                            if app['appId'] in apps_2021:
                                info_2021 = df_mhf.loc[df_mhf["App_Id"]==app['appId'], ["Required_IOS_Version", "Size_Bytes", "Average_User_Rating", "Reviews", "Price", "Currency"]].iloc[0,:].to_list()
                                info_2021 = [str(x) for x in info_2021]
                                write_app(app, info_2021)
                            else:
                                write_app(app, ['NA']*6)
                                
                        update_apps_queried(app['appId'])
                        update_apps_to_query(app['appId'])
                    
    # Step 5: Mark app as already queried reload


