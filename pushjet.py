from urllib.request import urlopen, Request
from requests import post

class PushJet(object):
    def __init__(self, config):
        self.secret = config.get('secret')

    def push(self, message):
        return post('https://api.pushjet.io/message', data={'secret': self.secret, 'message': message}).json()
