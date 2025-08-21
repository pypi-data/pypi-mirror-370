
import time

class Cache:
    def __init__(self, ttl_seconds=60*60):
        self.store = {}
        self.ttl = ttl_seconds

    def get(self, key):
        entry = self.store.get(key)
        if entry and entry['expiry'] > time.time():
            return entry['data']
        self.store.pop(key, None)
        return None

    def set(self, key, data):
        self.store[key] = {
            'data': data,
            'expiry': time.time() + self.ttl
        }

    def clear(self):
        self.store={}
