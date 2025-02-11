'''
Author: ChZheng
Date: 2025-02-12 04:42:00
LastEditTime: 2025-02-12 04:52:14
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/main.py
'''
# project/main.py
import uvicorn
from fastapi import FastAPI
from core.config import AppConfig
from api.routers import router

app = FastAPI(
    title="ABTest Proxy API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=AppConfig.LOG_LEVEL.lower()
    )
