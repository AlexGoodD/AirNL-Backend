from fastapi import FastAPI
from app.api.v1 import health, air

app = FastAPI(title="AirNL API")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(air.router, prefix="/aq", tags=["air"])