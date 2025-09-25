from fastapi import APIRouter
from . import air_current, air_forecast, stations, advice

router = APIRouter()

router.include_router(air_current.router)
router.include_router(air_forecast.router)
router.include_router(stations.router)
router.include_router(advice.router)