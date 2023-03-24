import datetime
from http_server_utils import *


class HTTPCache:
    def __init__(self):
        self.cache = {}
