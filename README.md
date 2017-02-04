# Anime Snake
Fetches new anime torrents automatically and notifies the user

I wanted a system that would automatically download the anime I cannot watch through (legal) streaming services and send a push to my cellphone when a new episode is available. I made it somewhat extensible.

It fetches the list of torrents from NyaaTorrents and adds torrent to transmission as new episodes are available. When the torrent is complete, it send a notification through PushBullet's API to my cell phone.

It scrapes the web page with Beautiful Soup 4. It uses transmission-rpc to communicate with a transmission daemon. It uses a SQLite database to store information about torrents. It's configurable through a YAML configuration file. It uses the JSON library to post requests to PushBullet's API.

## Dependencies
- JSON
- PyYAML
- sqlite3
- transmissionrpc
- urllib3

## Configuration
Configuration looks like this:

```YAML
pb_device:
pb_token:
series:
        - subber: 'HorribleSubs'
          name: 'Urara Meirochou'
          quality: '720p'
```

pb_device and pb_token are respectively the device identifier and Authorization Token used for the PushBullet API. series is a list, so you can put as many series as you want to download. 

You need to create a SQLite database file called anime.db beforehand. Use this query to create the episodes table:
```SQL
CREATE TABLE episodes(show text, number int, torhash text, complete int);
```

## To Do
There are many things I should do to make this system truly extensible (and not just an hackish scrapper coded overnight)
- Truly separate the scrapper, the torrent client, the database and the notifier part of the program
- Make the update delay and other variables configurable
- Properly document dependencies
