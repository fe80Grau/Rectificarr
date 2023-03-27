# Rectificarr
* Sometimes Torrent Trackers set shit names in movie files.
* This shit causes "Unable to parse file" or "Unknown Movie" error in Radarr Activity, then Radarr can't rewrite file to setted Path.
* This script uses Radarr API to check if exist an activity with this error and force rename
* Optional, This project contains posttorrent.sh Bash script integrated with Transmission Daemon to auto-unrar torrent downloads. 

## Requirements
* Python3
* Transmission Daemon
* Radarr
* Radarr API Key

## Installation
* I recommend /opt/ in Linux or C:\ProgramData in Windows, to allocate Rectificarr.
* The next steps are tested over Ubuntu 22.04 LTS
```console
cd /opt && git clone https://github.com/fe80Grau/Rectificarr.git
```

> ## Rectificarr
> * Edit config.json with your values. (To found Radarr API Key go to Radarr web interface -> Settings -> General -> Show Advanced -> Search for API Key in Security section).
> * Save it
> * Check if is it working. 
> ```console
> /usr/bin/python3 /opt/Rectificarr/main.py
> ```
> * If don't error presents, it's ok
> * Add cronjob with root privileges. Each 2 hours Python3 runs Rectificarr script. (Edit cron values if you want another interval)
> ```console
> cd /etc/cron.d &&
> sudo echo "00 */2 * * * root /usr/bin/python3 /opt/Rectificarr/main.py" > rectificarr
> ```

> ## posttorrent.sh / after download unrar for Transmission (Only for Linux)
> * To make the script work you have to add/change these lines in a configuration file named "settings.json" (usually /etc/transmission-daemon/settings.json).
> ```json
> "script-torrent-done-enabled": true, 
> "script-torrent-done-filename": "/opt/Rectificarr/posttorrent.sh", 
> ```
> * Reload Transmission Daemon. To set new settins.json, important to use next command. (If you uses service or systemcl your changes in settings.json will be not applied, and will be replaced with old values)
> ```console
> invoke-rc.d transmission-daemon reload
> ```

## Credits
[![GitHub - ShieldsIO](https://img.shields.io/badge/GitHub-ShieldsIO-42b983?logo=GitHub)](https://github.com/badges/shields)
[![GitHub - Transmission](https://img.shields.io/badge/GitHub-Transmission-D70008?logo=GitHub)](https://github.com/transmission/transmission)
[![GitHub - Radarr](https://img.shields.io/badge/GitHub-Radarr-ffc230?logo=GitHub)](https://github.com/Radarr/Radarr)
[![Transmission Forum - Killemov](https://img.shields.io/badge/Transmission_Forum-Killemov-4692BF)](https://forum.transmissionbt.com/viewtopic.php?t=10364)
