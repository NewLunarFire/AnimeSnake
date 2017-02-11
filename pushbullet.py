from urllib.request import urlopen, Request
from json import dumps

class PushBullet(object):
    def __init__(self, config):
        self.device = config.get('device')
        self.token = config.get('token')

    def push(self, message):
        data = dumps({"device_iden": self.device, "type": "note", "title": "Anime Snake", "body": message}).encode('utf-8')
        req = Request('https://api.pushbullet.com/v2/pushes')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.add_header('Access-Token', self.token)
        req.add_header('Content-Length', len(data))
        urlopen(req, data)
