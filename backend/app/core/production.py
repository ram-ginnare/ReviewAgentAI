from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from fastapi import Request
from fastapi.responses import JSONResponse

class SlidingWindowRateLimiter:
    def __init__(self, limit:int, window_seconds:int):
        self.limit=limit; self.window=window_seconds; self._data=defaultdict(deque); self._lock=Lock()
    def allow(self,key:str)->bool:
        now=monotonic()
        with self._lock:
            q=self._data[key]
            while q and now-q[0]>=self.window: q.popleft()
            if len(q)>=self.limit: return False
            q.append(now); return True

async def enforce_rate_limit(request: Request, call_next, limiter: SlidingWindowRateLimiter):
    if request.url.path in {'/','/api/v1/health'} or request.method=='OPTIONS':
        return await call_next(request)
    key=f'{request.client.host if request.client else "unknown"}:{request.url.path}'
    if not limiter.allow(key):
        return JSONResponse(status_code=429, content={'detail':'Too many requests. Please try again later.','code':'RATE_LIMITED'}, headers={'Retry-After':str(limiter.window)})
    return await call_next(request)
