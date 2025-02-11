'''
Author: ChZheng
Date: 2025-02-12 04:40:02
LastEditTime: 2025-02-12 04:52:01
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/api/routers.py
'''
# project/api/routers.py
from fastapi import APIRouter, Depends, HTTPException
from .schemas import ExperimentCreateRequest, ExperimentResponse, ErrorResponse
from .dependencies import get_abtest_service

router = APIRouter()

@router.post(
    "/experiments",
    response_model=ExperimentResponse,
    responses={500: {"model": ErrorResponse}}
)
async def create_experiment(
    request: ExperimentCreateRequest,
    service: ABTestService = Depends(get_abtest_service)
):
    try:
        response_data = service.create_experiment(request.dict())
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": 500,
                "message": "Internal Server Error",
                "detail": str(e)
            }
        )

@router.get("/healthcheck")
async def health_check():
    return {"status": "ok"}