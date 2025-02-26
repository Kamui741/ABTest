# clients/v2_client.py 修改URL生成逻辑
from typing import Dict, Any, Optional
from interfaces import IApiClient
from api.helpers import post_data, fetch_data, put_data
from config import config
# TODO: 分离功能函数
class V2Client(IApiClient):
    """适配config.py的V2客户端实现"""

    def create_experiment(self, params: Dict) -> Dict:
        required_fields = ['name', 'mode', 'app_id', 'duration',
                         'major_metric', 'metrics', 'versions']
        if missing := [f for f in required_fields if f not in params]:
            return self._error_response(f"缺少必要字段: {missing}")

        return post_data(
            url=self._build_url('create_experiment', app_id=params['app_id']),
            json_data={
                "name": params["name"],
                "mode": params["mode"],
                "endpoint_type": params["endpoint_type"],
                "duration": params["duration"],
                "major_metric": params["major_metric"],
                "metrics": params["metrics"],
                "versions": self._build_versions(params["versions"]),
                "layer_info": params.get("layer_info", {"layer_id": -1})
            },
            auth_type='v2'
        )

    def get_experiment_details(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('get_details',
                app_id=params['app_id'],
                experiment_id=params['experiment_id']
            ),
            auth_type='v2'
        )

    def generate_report(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('generate_report',
                app_id=params['app_id'],
                experiment_id=params['experiment_id']
            ),
            params={
                "report_type": params['report_type'],
                "start_ts": params['start_ts'],
                "end_ts": params['end_ts'],
                "filters": params.get("filters", ""),
            },
            auth_type='v2'
        )

    def modify_experiment_status(self, params: Dict) -> Dict:
        valid_actions = ["launch", "stop"]
        if params['action'] not in valid_actions:
            return self._error_response(f"无效操作, 可选值: {valid_actions}")

        return put_data(
            url=self._build_url('modify_status',
                app_id=params['app_id'],
                experiment_id=params['experiment_id'],
                action=params['action']
            ),
            auth_type='v2'
        )

    def list_metrics(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('list_metrics', app_id=params['app_id']),
            params={
                "keyword": params.get('keyword', ''),
                "page": params.get('page', 1),
                "page_size": params.get('page_size', 10)
            },
            auth_type='v2'
        )

    def list_groups(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('list_groups', app_id=params['app_id']),
            params={
                "need_page": params.get("need_page", 1),
                "page": params.get('page', 1),
                "page_size": params.get('page_size', 10)
            },
            auth_type='v2'
        )

    def _build_url(self, endpoint_name: str,**path_params) -> str:
        """使用config配置生成完整URL"""
        base_url = config.BASE_URLS['V2']
        endpoint_template = config.API_ENDPOINTS[endpoint_name]['V2']
        return f"{base_url}/{endpoint_template.format(**path_params)}"


    def _build_versions(self, versions: list) -> list:
        return [{
            "type": v["type"],
            "name": v["name"],
            "description": v.get("description", ""),  # 补全文档字段
            "weight": v.get("weight", 50),  # 处理weight逻辑
            "config": v.get("config", {}),  # 直接透传
            "users": v.get("users", [])
        } for v in versions]

    def _error_response(self, message: str) -> Dict:
        return {"code": 400, "message": message}