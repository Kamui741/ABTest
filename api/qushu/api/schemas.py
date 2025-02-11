'''
Author: ChZheng
Date: 2025-02-12 04:40:11
LastEditTime: 2025-02-12 04:51:22
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/api/schemas.py
'''
# project/api/schemas.py
from pydantic import BaseModel
from typing import List, Dict

class ExperimentCreateRequest(BaseModel):
    name: str
    duration_days: int
    app_id: int
    versions: List[Dict[str, str]]

class ExperimentResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    versions: List[Dict]

class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None