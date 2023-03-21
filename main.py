#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------

# Sometimes Torrent Trackers set shit names in movie files. 
# This shit causes "Unable to parse file" error in Radarr Activity, then Radarr can't rewrite file to setted Path.
# This script uses Radarr API to check if exist an activity with this error and force rename
# This project contains posttorrent.sh Bash script integrated with Transmission Daemon to auto-unrar torrent downloads. 
# posttorrent.sh Credits to Killemov. Instructions : https://forum.transmissionbt.com/viewtopic.php?t=10364
#
# Rectificarr
# Created By  : fe80grau
# Created Date: 2023/02
# version ='1.0'
# Radarr API : https://radarr.video/docs/api/
# Radarr API Endpoint used in this script: https://radarr.video/docs/api/#/Queue/get_api_v3_queue
# isBase64 function from: https://stackoverflow.com/questions/12315398/check-if-a-string-is-encoded-in-base64-using-python
# -------------------------------------------

import requests
import urllib.parse
import shutil
import traceback
import base64
import json
import os
import mimetypes
import glob

#Reading config file
with open('config.json', 'r') as f:
    config = json.load(f)

#Utils
def makeUrl(host, port, endpoint, params):
    baseurl = "http://{}:{}/".format(host, port)
    return "{}{}?{}".format(baseurl, endpoint, params)

def rename(title, year, quality, file):
    return "{} ({}) {}.{}".format(title, year, quality, file.split('.')[-1])

#Define Radarr setting and enpoint url constructor 
#Queue
params_radarr = urllib.parse.urlencode({
    "includeUnknownMovieItems" : "true",
    "includeMovie" : "true",
    "apikey" : config['radarr']['api_key']
})
#Make url merging chunks with makeUrl util
queue_url_radarr = makeUrl(config['radarr']['host'], 
                            config['radarr']['port'],
                            'api/v3/queue',
                            params_radarr)

#Get list of all movies /api/v3/movie amd merging history
movies_history = []
params_radarr = urllib.parse.urlencode({
    "apikey" : config['radarr']['api_key']
})

movies_url_radarr = makeUrl(config['radarr']['host'], 
                            config['radarr']['port'],
                            'api/v3/movie',
                            params_radarr)

movies = requests.get(movies_url_radarr).json()
for movie in movies:
    params_radarr = urllib.parse.urlencode({
        "movieid" : movie['id'],
        "apikey" : config['radarr']['api_key']
    })

    #Get history for movie item
    history_url_radarr = makeUrl(config['radarr']['host'],
                                 config['radarr']['port'],
                                 'api/v3/history/movie',
                                 params_radarr)
    
    histories = requests.get(history_url_radarr).json()
    downloadsIds = []
    for history in histories:
        if 'downloadId' in history:
            downloadsIds.append(history['downloadId'])

    data = {
        "id" : movie['id'],
        "title" : movie['title'],
        "year" : movie['year'],
        "path" : movie['path'],
        "downloadIds" : downloadsIds
    }

    movies_history.append(data)

#MAIN
if __name__ == "__main__":
    #Call url_radarr with GET 
    data = requests.get(queue_url_radarr).json()

    print("Rectificarr is running...")

    #Activities in Radarr shows in records key (list)
    #An activity is a download/rewrite process. A movie can be download many times with differents torrent tyrs, each download is an activity.
    if 'records' in data:
        print('Processing data from Radarr')
        print('{}'.format(queue_url_radarr))

        #Loop Activies
        for item in data['records']:

            #Check if statusMessages is setted. If not, this code will initilice a fake values to avoid errors and keep minimal code
            if len(item['statusMessages']) < 1:
                item['statusMessages'] = [{'messages'  : [''], 'title':''}]

            trackedDownloadStatus = item['trackedDownloadStatus']
            trackedDownloadState = item['trackedDownloadState']
            statusMessage = item['statusMessages'][0]['messages'][0]  

            if not "wasn't grabbed by Radarr" in statusMessage:
                if not 'movieId' in item:
                    for mh in movies_history:
                        if item['downloadId'] in mh['downloadIds']:
                            item['movieId'] = mh['id']
                            item['movie'] = {
                                "title" : mh['title'],
                                "year" : mh['year'],
                                "path" : mh['path']
                            }
                            break
                    
                    if not 'movieId' in item:
                        break
                
                #Getting data from Activity
                queue_id = item['id']
                downloadId = item['downloadId']
                movieId = item['movieId']
                title = item['movie']['title']
                year = str(item['movie']['year'])
                path = item['movie']['path']
                quality = item['quality']['quality']['name']
                source = item['outputPath']
                file_source = item['statusMessages'][0]['title']

                #If the movie is in a folder
                if not os.path.isfile(source + "/" + file_source):
                    for f in os.listdir(source):
                        if os.path.isfile(os.path.join(source, f)):
                            file_source = f

                #Print movie title to debug
                print("||||| {}".format(title))

                #Check conditions to ensure that "Unable to parse file" error in statusMessage depends to importPending trackedDownloadState
                if trackedDownloadStatus == 'warning' \
                and trackedDownloadState == 'importPending' \
                and (statusMessage == 'Unable to parse file' or statusMessage == 'Unknown Movie') :
                    #Print movieId and absolute path to debug
                    print("|||||||||| Movie warning detectect: {} - {}/{}".format(movieId, title, file_source))
                    print("- Trying to rename and move to correct folder")
                    #Trying to make a new_name and rewrite in source. After that, Radarr automaticaly will detect this change and can parse the file.
                    try:
                        new_name = rename(title, year, quality, file_source)
                        print("- Old name: {}".format(file_source))
                        print("- New name: {}".format(new_name))

                        #Quick patch to solve https://github.com/fe80Grau/Rectificarr/issues/2
                        if os.path.isfile(source):
                            mv_source = source
                            mv_new = source.replace(source.split('/')[-1], new_name)
                        else:                                
                            mv_source = source + "/" + file_source
                            mv_new = source + "/" + new_name

                        #shutil.move(mv_source, mv_new)

                        #Copy file to Radarr defined movie path
                        print("|||||Importing movie... ")
                        if not os.path.isfile("{}/{}".format(path, new_name)):
                            shutil.copy(mv_source, "{}/{}".format(path, new_name))
                        
                        params_radarr = urllib.parse.urlencode({
                            "folder" : "{}/{}".format(path, new_name),
                            "downloadId" : downloadId,
                            "movieid" : movieId,
                            "apikey" : config['radarr']['api_key']
                        })
                        manual_import_radarr = makeUrl(config['radarr']['host'],
                                                        config['radarr']['port'],
                                                        'api/v3/manualimport',
                                                        params_radarr)
                        manual_import_result = requests.get(manual_import_radarr).json()
                        print(manual_import_result)
                        print("import done")

                        #Rescan movie with /api/command?name=RescanMovie?movieId={movieId}
                        print("|||||Rescanning movie... ")
                        params_radarr = urllib.parse.urlencode({
                            "movieid" : movieId,
                            "apikey" : config['radarr']['api_key']
                        })                        
                        command_url_radarr = makeUrl(config['radarr']['host'],
                                                        config['radarr']['port'],
                                                        'api/v3/command',
                                                        params_radarr)
                        command_result = requests.get(command_url_radarr).json()
                        print("Rescan done")

                        print("|||||Deleting in queue...")
                        params_radarr = urllib.parse.urlencode({
                            "apikey" : config['radarr']['api_key']
                        })                        
                        delete_url_radarr = makeUrl(config['radarr']['host'],
                                                        config['radarr']['port'],
                                                        'api/v3/queue/{}'.format(queue_id),
                                                        params_radarr)
                        delete_result = requests.delete(delete_url_radarr, data=json.dumps(params_radarr)).json()
                        print(delete_result)
                        print("Delete done")
                    except Exception:
                        traceback.print_exc()
    #If endpoints fails...          
    else:
        print('No data found')
