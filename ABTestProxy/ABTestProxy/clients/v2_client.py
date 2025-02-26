# ---------------------- clients/v2_client.py ----------------------
import requests
from typing import Dict, Any
from interfaces import IApiClient
from config import config

class V2Client(IApiClient):
    """完整的V2客户端实现"""

    def create_experiment(self, app_id: int, params: Dict) -> Dict:
        """
        创建实验
        接口路径：POST /openapi/v2/apps/{app_id}/experiments
        """
        endpoint = config.get_endpoint('create_experiment').format(app_id=app_id)
        required_fields = ['name', 'mode', 'endpoint_type', 'duration',
                         'major_metric', 'metrics', 'versions']

        if not all(field in params for field in required_fields):
            return self._error_response("Missing required fields")

        payload = {
            "name": params["name"],
            "mode": params["mode"],
            "endpoint_type": params["endpoint_type"],
            "duration": params["duration"],
            "major_metric": params["major_metric"],
            "metrics": params["metrics"],
            "versions": self._build_versions(params["versions"]),
            "layer_info": params.get("layer_info", {"layer_id": -1}),
            "description": params.get("description", "")
        }
        return self._send_request('POST', endpoint, payload)

    def get_details(self, app_id: int, experiment_id: int) -> Dict:
        """
        获取实验详情
        接口路径：GET /openapi/v2/apps/{app_id}/experiments/{experiment_id}
        """
        endpoint = config.get_endpoint('get_details').format(
            app_id=app_id,
            experiment_id=experiment_id
        )
        return self._send_request('GET', endpoint, {})

    def generate_report(self, app_id: int, experiment_id: int,
                      report_type: str, start_ts: int, end_ts: int) -> Dict:
        """
        生成实验报告
        接口路径：GET /openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics
        """
        endpoint = config.get_endpoint('generate_report').format(
            app_id=app_id,
            experiment_id=experiment_id
        )
        params = {
            "report_type": report_type,
            "start_ts": start_ts,
            "end_ts": end_ts
        }
        return self._send_request('GET', endpoint, params)

    def modify_status(self, app_id: int, experiment_id: int, action: str) -> Dict:
        """
        修改实验状态
        接口路径：PUT /openapi/v2/apps/{app_id}/experiments/{experiment_id}/[launch|stop]
        """
        valid_actions = ["launch", "stop"]
        if action not in valid_actions:
            return self._error_response(f"Invalid action. Valid options: {valid_actions}")

        endpoint = config.get_endpoint('modify_status').format(
            app_id=app_id,
            experiment_id=experiment_id,
            action=action
        )
        return self._send_request('PUT', endpoint, {})

    def list_metrics(self, app_id: int, keyword: str = "",
                   page: int = 1, page_size: int = 10) -> Dict:
        """
        获取指标列表
        接口路径：GET /openapi/v2/apps/{app_id}/metrics
        """
        endpoint = config.get_endpoint('list_metrics').format(app_id=app_id)
        params = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        return self._send_request('GET', endpoint, params)

    def list_groups(self, app_id: int, keyword: str = "",
                  page: int = 1, page_size: int = 10) -> Dict:
        """
        获取互斥组列表
        接口路径：GET /openapi/v2/apps/{app_id}/layers
        """
        endpoint = config.get_endpoint('list_groups').format(app_id=app_id)
        params = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size
        }
        return self._send_request('GET', endpoint, params)

    def _build_versions(self, versions: list) -> list:
        """构建版本数据"""
        return [{
            "type": v["type"],
            "name": v["name"],
            "description": v.get("description", ""),
            "weight": v.get("weight"),
            "config": v["config"],
            "users": [{
                "ssids": user.get("ssids", []),
                "type": user.get("type", "id")
            } for user in v.get("users", [])]
        } for v in versions]