# Library imports
from urllib.request import urlopen, urlretrieve, Request
from bs4 import BeautifulSoup
from yaml import load
from os import getcwd
import transmissionrpc
import re
import sqlite3
import sched
from time import time, sleep
import json

# Local Imports
from pushbullet import PushBullet
from pushjet import PushJet

# YAML Config
config = load(open('config.yaml', 'r'))

if config.get('pushservice') == 'pushbullet':
    pusher = PushBullet(config.get('pushbullet'))
elif config.get('pushservice') == 'pushjet':
    pusher = PushJet(config.get('pushjet'))

#Connect to animu database
conn = sqlite3.connect('anime.db')
cursor = conn.cursor()

#Useful Regex for extracting information from shows
exp = re.compile('\[(\w+)\] ([\w|\s]+) - (\d+(v\d)?) \[(\d+)p\]')

# RPC Client for Transmission BitTorrent
tc = transmissionrpc.Client('localhost', port=9091, user='transmission', password='transmission')

# Scheduler to execute the tasks at regular intervals
scheduler = sched.scheduler(time, sleep)

# Get Torrent for selected shows
def getEpisodes(show):
    episodeList = [];
    term = "[{subber}]+{name}+[{quality}]".format(subber=show.get("subber"), name=show.get("name"), quality=show.get("quality")).replace(" ", "+")
    html = urlopen("https://www.nyaa.se/?page=search&term=" + term).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    for row in soup.find_all("tr", class_="tlistrow"):
        name = row.find("td", class_="tlistname").a.string
        url = "http:" + row.find("td", class_="tlistdownload").a.get("href")
        mtch = exp.match(name)
        if mtch != None:
            episodeList.append(dict(number = mtch.group(3), url = url))
   
    return episodeList

# Add a torrent to the transmission daemon
def addTorrent(show, episode):
    filename = getcwd() + "/" + show.get("name") + "-" + episode.get("number") + ".torrent"
    urlretrieve(episode.get("url"), filename)
    hashStr = tc.add_torrent(filename).hashString
    cursor.execute("INSERT INTO episodes VALUES(?, ?, ?, ?)", (show.get("name"), episode.get("number"), hashStr, 0))

# Look for update on shows
def updateShows():
    print("Updating")
    for show in config.get("series"):
        for ep in getEpisodes(show):
            row = cursor.execute("SELECT * FROM episodes WHERE show=? AND number=? LIMIT 1", (show.get("name"), ep.get("number"))).fetchone()
            if row == None:
                print("Adding {show} - {num} in database".format(show= show.get("name"), num = ep.get("number")))
                addTorrent(show, ep)
            else:
                if row[3] == 0:
                    torrent = tc.get_torrent(row[2])
                    if(torrent.percentDone == 1.0):
                        # Episode finished downloading, send PushBullet
                        print("{show} - {num} finished downloading".format(show= show.get("name"), num = ep.get("number")))
                        pusher.push("{show} - Episode {num} has finished downloading".format(show = show.get("name"), num = ep.get("number")))
                        cursor.execute("UPDATE episodes SET complete=1 WHERE show=? AND number=?", (show.get("name"), ep.get("number")))
    
    # Commit changes to database 
    conn.commit()

    # Reschedule in 15 minutes
    scheduler.enter(15 * 60, 1, updateShows, ())
    print("Next update is in 15 minutes")
    return

scheduler.enter(0, 1, updateShows, ())
scheduler.run()
