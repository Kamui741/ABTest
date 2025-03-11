'''
Author: ChZheng
Date: 2025-03-05 15:19:27
LastEditTime: 2025-03-10 17:06:29
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/ABTestProxy/app.py
'''
# ---------------------- app.py ----------------------
# app.py
from fastapi import FastAPI, Path, Query, Body, HTTPException, Request
import logging
import re
from typing import Optional, Dict, Any
from service import ABTestService

app = FastAPI(title="ABTest API Service", version="2.0")
logger = logging.getLogger(__name__)

# -------------------- API Endpoints --------------------
@app.post("/openapi/{version}/apps/{app_id}/experiments",
          summary="创建实验",
          tags=["实验管理"])
async def create_experiment(
    request: Request,
    app_id: int = Path(..., description="应用ID"),
    version: str = Path(..., description="API版本控制参数")
):
    """创建新实验（支持V1/V2双版本）"""

    # 解析请求体
    body_data = await request.json()
    # 构建参数
    params = {
        "app_id": app_id,
        "version": version,
        **body_data
    }

    result = ABTestService().create_experiment(params)
    return handle_response(result)



@app.get("/openapi/{version}/apps/{app_id}/experiment/{experiment_id}/details",
         summary="获取实验详情",
         tags=["实验管理"])
async def get_experiment_details(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    version: str = Path(..., description="API版本控制参数")
):
    """获取实验配置详情"""

    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "version": version
    }
    result = ABTestService().get_experiment_details(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/experiment/{experiment_id}/metrics",
         summary="生成实验报告",
         tags=["实验分析"])
async def generate_report(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    report_type: str = Query(..., description="报告类型: day/hour/five_minute"),
    start_ts: str = Query(..., description="开始时间戳（10位）"),
    end_ts: str = Query(..., description="结束时间戳（10位）"),
    filters: Optional[str] = Query(None, description="过滤条件"),
    version: str = Path(..., description="API版本控制参数")
):
    """生成实验指标报告"""
    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "report_type": report_type,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "filters": filters,
        "version": version
    }
    result = ABTestService().generate_report(params)
    return handle_response(result)


@app.put("/openapi/{version}/apps/{app_id}/experiments/{experiment_id}/{action}",
         summary="修改实验状态",
         tags=["实验管理"])
async def modify_experiment_status(
    app_id: int = Path(..., description="应用ID"),
    experiment_id: int = Path(..., description="实验ID"),
    action: str = Path(..., description="操作类型: launch/stop"),
    version: str = Path(..., description="API版本控制参数")
):
    """启动/停止实验"""

    params = {
        "app_id": app_id,
        "experiment_id": experiment_id,
        "action": action,
        "version": version
    }
    result = ABTestService().modify_experiment_status(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/metrics",
         summary="获取指标列表",
         tags=["资源管理"])
async def list_metrics(
    app_id: int = Path(..., description="应用ID"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    page: int = Query(1, ge=1, description="当前页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    need_page: int = Query(1, ge=0, le=1, description="是否分页"),
    version: str = Path(..., description="API版本控制参数")
):
    """查询可用指标"""

    params = {
        "app_id": app_id,
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "need_page": need_page,
        "version": version
    }
    result = ABTestService().list_available_metrics(params)
    return handle_response(result)


@app.get("/openapi/{version}/apps/{app_id}/layers",
         summary="获取互斥组列表",
         tags=["资源管理"])
async def list_mutex_groups(
    app_id: int = Path(..., description="应用ID"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    page: int = Query(1, ge=1, description="当前页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    need_page: int = Query(1, ge=0, le=1, description="是否分页"),
    version: str = Path(..., description="API版本控制参数")
):
    """查询互斥组信息"""

    params = {
        "app_id": app_id,
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
        "need_page": need_page,
        "version": version
    }
    result = ABTestService().list_mutex_groups(params)
    return handle_response(result)


# -------------------- 工具函数 --------------------
def handle_response(result: Dict) -> Dict:
    """统一响应处理"""
    if result.get("code") == 200:
        return {
            "code": 200,
            "message": "success",
            "data": result.get("data", {})
        }
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "code": result.get("code", 500),
                "message": result.get("message", "未知错误")
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



# TODO: restful api
