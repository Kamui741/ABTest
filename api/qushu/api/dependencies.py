'''
Author: ChZheng
Date: 2025-02-12 04:48:21
LastEditTime: 2025-02-12 04:51:43
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/api/dependencies.py
'''
'''
# project/api/dependencies.py
from fastapi import Depends
from .services import ABTestService
from core.mapper import FieldMapper

def get_abtest_service() -> ABTestService:
    return ABTestService()

def get_field_mapper() -> FieldMapper:
    return FieldMapper()