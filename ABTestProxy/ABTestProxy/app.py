'''
Author: ChZheng
Date: 2025-03-05 15:19:27
LastEditTime: 2025-03-05 17:10:55
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/app.py
'''
# ---------------------- app.py ----------------------
from fastapi import FastAPI, Depends
from service import ABTestService

app = FastAPI()

@app.post("/experiments")
async def create_exp(params: dict, service: ABTestService = Depends()):
    return service.create_experiment(params)

@app.get("/experiments/{exp_id}")
async def get_exp(exp_id: str, service: ABTestService = Depends()):
    return service.get_experiment(exp_id)

# TODO: v1 v2 参数导入
# TODO: ip 提取为公共参数
# TODO: 暴露 web 接口
# TODO: mock 测试
# TODO: main 函数只需要一个版本
# TODO: restful api
