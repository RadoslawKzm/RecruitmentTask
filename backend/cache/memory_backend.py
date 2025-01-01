import time


class MemoryBackend:
    def __init__(self):
        super().__init__()
        self.cache = {}

    async def create(self, response_body, key: str, ex: int = 60):
        self.cache[key] = {
            "data": response_body,
            "expire": time.time() + ex,
        }

    async def retrieve(self, key: str):
        try:
            data = self.cache[key]["data"]
            expire = self.cache[key]["expire"]
        except KeyError:
            return None
        if expire >= time.time():
            return data, expire - time.time()

    def invalidate(self, key: str):
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()
