from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=5, window=60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path.startswith("/predict"):
            client_ip = request.client.host
            now = time.time()
            timestamps = self.clients.get(client_ip, [])

            # Clean up expired timestamps
            timestamps = [t for t in timestamps if now - t < self.window]

            if len(timestamps) >= self.max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            timestamps.append(now)
            self.clients[client_ip] = timestamps

        response = await call_next(request)
        return response
