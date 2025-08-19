import aiohttp
import time
from collections import OrderedDict

class SafeSubsClient:
    def __init__(
        self,
        api_token: str,
        api_url: str = "https://subs.sxve.it/v1/check",
        ttl_minutes: int = 24 * 60,
        max_size: int = 100_000
    ):
        self.api_token = api_token
        self.api_url = api_url
        self.default_ttl = ttl_minutes * 60
        self.max_size = max_size
        self._cache: OrderedDict[int, tuple[bool, float]] = OrderedDict()

    def _clean_cache(self, now: float):
        # удаляем протухшие ключи
        keys_to_delete = [uid for uid, (_, expires_at) in self._cache.items() if expires_at <= now]
        for uid in keys_to_delete:
            self._cache.pop(uid)

        # ограничиваем размер кеша
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # удаляем самый старый

    async def __call__(self, user_id: int) -> bool:
        now = time.time()
        self._clean_cache(now)

        cached = self._cache.get(user_id)
        if cached:
            value, expires_at = cached
            if expires_at > now:
                return value
            else:
                self._cache.pop(user_id)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                json={"user_id": user_id, "auth_token": self.api_token}
            ) as resp:
                if resp.status != 200:
                    return False

                data = await resp.json()
                result = data.get("status", False)

                if result:
                    ttl_minutes = data.get("cache_ttl", self.default_ttl // 60)
                    expires_at = now + ttl_minutes * 60
                    self._cache[user_id] = (True, expires_at)

                return result
