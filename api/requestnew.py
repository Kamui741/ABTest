import requests
import os
import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from functools import wraps

# ================== 基础配置 ==================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================== 一期功能实现 ==================
class SessionManager:
    """一期会话管理器（原有实现）"""
    def __init__(self, login_url: str, session_file: str):
        self.login_url = login_url
        self.session_file = session_file

    # ... 原有方法保持不变 ...
    # 为保持代码简洁，此处省略具体实现，实际开发中需保留完整代码

def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """一期创建实验方法（原有实现）"""
    # ... 原有四步请求流程 ...
    return step4_response

def update_flight_status(flight_id: int, action: str) -> Optional[Dict]:
    """一期修改实验状态方法（原有实现）"""
    # ... 原有实现逻辑 ...
    return response

def get_flight_config(flight_id: int, is_duplicate: bool = False) -> Optional[Dict]:
    """一期获取实验配置（待实现）"""
    # TODO: 等待一期实现
    pass

# ================== 二期接口适配层 ==================
class ABTestV2Service:
    """二期服务入口类"""
    def __init__(self, v1_adapter):
        self.v1_adapter = v1_adapter

    def create_experiment_v2(self,
                           app_id: int,
                           name: str,
                           mode: int,
                           endpoint_type: int,
                           duration: int,
                           major_metric: int,
                           metrics: List[int],
                           versions: List[Dict],
                           layer_info: Dict,
                           description: Optional[str] = None) -> Dict:
        """二期创建实验主入口"""
        self._validate_create_params(mode, endpoint_type, duration, major_metric, metrics, versions)
        return self.v1_adapter.create_experiment_v2_proxy(
            app_id=app_id,
            name=name,
            mode=mode,
            endpoint_type=endpoint_type,
            duration=duration,
            major_metric=major_metric,
            metrics=metrics,
            versions=versions,
            layer_info=layer_info,
            description=description
        )

    def update_experiment_status_v2(self, app_id: int, experiment_id: int, action: str) -> Dict:
        """二期修改实验状态"""
        if action not in ("launch", "stop"):
            return {"code": 400, "message": "Invalid action", "data": None}
        return self.v1_adapter.update_status_v2_proxy(
            app_id=app_id,
            experiment_id=experiment_id,
            action=action
        )

    def _validate_create_params(self, mode, endpoint_type, duration, major_metric, metrics, versions):
        """参数校验逻辑"""
        if mode != 1:
            raise ValueError("当前只支持实验类型为1")
        if endpoint_type not in (0, 1):
            raise ValueError("endpoint_type必须是0或1")
        if not (1 <= duration <= 365):
            raise ValueError("实验时长必须在1-365天之间")
        if major_metric not in metrics:
            raise ValueError("核心指标必须包含在指标列表中")
        if len(versions) < 2:
            raise ValueError("至少需要两个实验版本")

class V1Adapter:
    """一期适配转换器"""
    def __init__(self, v1_client):
        self.v1_client = v1_client

    # --------- 创建实验代理 ---------
    def create_experiment_v2_proxy(self, **v2_params) -> Dict:
        """创建实验参数转换"""
        try:
            v1_params = self._convert_create_params(v2_params)
            v1_response = self.v1_client.create_experiment(**v1_params)
            return self._convert_create_response(v1_response)
        except Exception as e:
            return self._format_error_response(str(e))

    def _convert_create_params(self, v2: Dict) -> Dict:
        """二期->一期参数结构转换"""
        return {
            "flight_name": v2['name'],
            "app_id": v2['app_id'],
            "duration": v2['duration'],
            "hash_strategy": "ssid",
            "major_metric": str(v2['major_metric']),
            "version_configs": [
                {
                    "type": ver['type'],
                    "name": ver['name'],
                    "weight": ver.get('weight', 0.5),
                    "config": ver['config']
                } for ver in v2['versions']
            ],
            "layer_info": json.dumps(v2.get('layer_info', {"layer_id": -1, "version_resource": 1.0})),
            "description": v2.get('description', '')
        }

    def _convert_create_response(self, v1_response: Dict) -> Dict:
        """一期->二期响应结构转换"""
        return {
            "code": 200 if v1_response.get('code') == 200 else 500,
            "message": v1_response.get('message', 'success'),
            "data": v1_response.get('data', {}).get('flight_id')
        }

    # --------- 状态修改代理 ---------
    def update_status_v2_proxy(self, **v2_params) -> Dict:
        """实验状态修改代理"""
        try:
            v1_params = self._convert_status_params(v2_params)
            v1_response = self.v1_client.update_flight_status(**v1_params)
            return self._convert_status_response(v1_response)
        except Exception as e:
            return self._format_error_response(str(e))

    def _convert_status_params(self, v2: Dict) -> Dict:
        return {
            "flight_id": v2["experiment_id"],
            "action": v2["action"]
        }

    def _convert_status_response(self, v1_response: Dict) -> Dict:
        return {
            "code": 200 if v1_response.get('code') == 200 else 500,
            "message": v1_response.get('message', 'success'),
            "data": {
                "operation_status": "SUCCESS" if v1_response.get('code') == 200 else "FAILED",
                "timestamp": datetime.now().isoformat()
            }
        }

    # --------- 通用工具方法 ---------
    def _format_error_response(self, error_msg: str) -> Dict:
        return {
            "code": 500,
            "message": f"Adapter Error: {error_msg}",
            "data": None
        }

# ================== 路由层（示例） ==================
from fastapi import APIRouter, Path

router = APIRouter()

@router.post("/openapi/v2/apps/{app_id}/experiments")
async def create_exp_v2(
    app_id: int = Path(...),
    request_data: Dict = Body(...)
):
    v2_service = ABTestV2Service(V1Adapter(SessionManager(...)))
    return v2_service.create_experiment_v2(app_id=app_id, **request_data)

@router.put("/openapi/v2/apps/{app_id}/experiments/{experiment_id}/launch/")
async def launch_exp_v2(
    app_id: int = Path(...),
    experiment_id: int = Path(...)
):
    v2_service = ABTestV2Service(V1Adapter(SessionManager(...)))
    return v2_service.update_experiment_status_v2(
        app_id=app_id,
        experiment_id=experiment_id,
        action="launch"
    )

# ================== 使用示例 ==================
if __name__ == "__main__":
    # 初始化适配器
    v1_session = SessionManager(login_url="...", session_file="...")
    adapter = V1Adapter(v1_session)

    # 创建二期服务实例
    v2_service = ABTestV2Service(adapter)

    # 测试创建实验
    test_params = {
        "app_id": 10000305,
        "name": "二期测试实验",
        "mode": 1,
        "endpoint_type": 1,
        "duration": 30,
        "major_metric": 29806,
        "metrics": [29806],
        "versions": [
            {"type": 0, "name": "对照组", "config": {"key": "A"}},
            {"type": 1, "name": "实验组", "config": {"key": "B"}}
        ],
        "layer_info": {"layer_id": -1, "version_resource": 0.5}
    }
    print(v2_service.create_experiment_v2(**test_params))

    # 测试修改状态
    print(v2_service.update_experiment_status_v2(
        app_id=10000305,
        experiment_id=12345,
        action="launch"
    ))