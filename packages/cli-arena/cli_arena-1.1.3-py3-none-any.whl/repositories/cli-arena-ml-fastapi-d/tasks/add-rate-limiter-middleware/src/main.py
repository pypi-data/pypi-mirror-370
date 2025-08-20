from fastapi import FastAPI
from src.middleware.rate_limiter import RateLimiter

app = FastAPI()
app.add_middleware(RateLimiter)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/predict")
async def predict():
    return {"prediction": "sample prediction"}
