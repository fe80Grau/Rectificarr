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

#Reading config file
with open('config.json', 'r') as f:
    config = json.load(f)

#Define Radarr setting and enpoint url constructor 

#Queue
apikey_radarr = config['radarr']['api_key']
baseurl_radarr = "http://{}:{}/api/v3/".format(config['radarr']['host'], config['radarr']['port'])
endpoint_radarr = "queue"
params_radarr = urllib.parse.urlencode({
    "includeUnknownMovieItems" : "true",
    "includeMovie" : "true",
    "apikey" : apikey_radarr
})

#Make url merging chunks
queue_url_radarr = baseurl_radarr + endpoint_radarr + "?" + params_radarr

#Get list of all movies /api/v3/movie amd merging history
movies_history = []

def rename(title, year, quality, file):
    return "{} ({}) {}.{}".format(title, year, quality, file.split('.')[-1])


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
                    #Search downloadId in movies_history
                    #si lo encuentra
                    #consutrir 
                        #item['movieId']
                        #item['movie']['title']
                        #item['movie']['year']
                        #item['movie']['path']
                        #item['quality']['quality']['name']

                    #si no
                    #break
                    

                #Getting data from Activity
                movieId = item['movieId']
                title = item['movie']['title']
                year = str(item['movie']['year'])
                path = item['movie']['path']
                quality = item['quality']['quality']['name']
                source = item['outputPath']
                file_source = item['statusMessages'][0]['title']

                #Print movie title to debug
                print("||||| {}".format(title))

                #Check conditions to ensure that "Unable to parse file" error in statusMessage depends to importPending trackedDownloadState
                if trackedDownloadStatus == 'warning' \
                and trackedDownloadState == 'importPending' \
                and (statusMessage == 'Unable to parse file') :
                    #Print movieId and absolute path to debug
                    print("|||||||||| Movie warning detectect: {} - {}/{}".format(movieId, title, file_source))
                    print("- Trying to rename and move to correct folder")
                    #Trying to make a new_name and rewrite in source. After that, Radarr automaticaly will detect this change and can parse the file.
                    try:
                        new_name = rename(title, year, quality, file_source)
                        print("- Old name: {}".format(file_source))
                        print("- New name: {}".format(new_name))

                        #Quick patch to solve https://github.com/fe80Grau/Rectificarr/issues/2
                        if(os.path.isfile(source)):
                            mv_source = source
                            mv_new = source.replace(source.split('/')[-1], new_name)
                        else:
                            mv_source = source + "/" + file_source
                            mv_new = source + "/" + new_name

                        shutil.move(mv_source, mv_new)

                        #Copy file to Radarr defined movie path

                        #Rescan movie with /api/command?name=RescanMovie?movieId={movieId}
                    except Exception:
                        traceback.print_exc()
    #If endpoints fails...          
    else:
        print('No data found')
