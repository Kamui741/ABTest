'''
Author: ChZheng
Date: 2025-03-05 14:53:48
LastEditTime: 2025-03-06 10:29:22
LastEditors: ChZheng
Description:
FilePath: /ABTest/ABTestProxy/src/clients.py
'''
# ---------------------- clients.py ----------------------
import logging
import uuid
from typing import Dict , Any , Optional
import requests
from config import config
from helpers import post_data , put_data , fetch_data

logger = logging.getLogger(__name__)

class BaseClient:
    """客户端基类"""
    def __init__(self, base_url: str, auth_type: str):
        self.base_url = base_url
        self.auth_type = auth_type



class V1Client(BaseClient):
    """V1客户端完整实现"""
    def __init__(self):
        super().__init__(
            base_url=config.BASE_URLS['V1'],
            auth_type='v1'
        )
    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（参数需适配V1格式）"""
        flight_name=params['flight_name']
        duration=params['duration']
        hash_strategy=params.get('hash_strategy', 'ssid')
        app_id=params['app_id']
        """
        创建实验的完整流程,包含四次连续的 POST 请求。
        """
        # Step 1: 初始化实验草稿
        step1_url = f"{self.base_url}/api/step1"
        step1_payload = {
            "flight_name": flight_name,
            "duration": duration,
            "hash_strategy": hash_strategy,
            "expiration_remind": True,
            "longrun_remind": True,
            "report_mode": 0,
            "mode": 1,
            "app": app_id
        }
        step1_response = post_data(step1_url, json_data=step1_payload)
        if not step1_response:
            logger.error(" 第一步请求失败")
            return None
        draft_id = step1_response.get("data",{}).get("draft_id")

        # Step 2: 配置实验指标
        step2_url = f"{self.base_url}/api/step2"
        step2_payload = {
            "major_metric": "1545",
            "metrics": "1545",
            "app": app_id,
            "draft_id": draft_id
        }
        step2_response = post_data(step2_url, json_data=step2_payload)
        if not step2_response:
            logger.error(" 第二步请求失败")
            return None

        # Step 3: 配置实验版本
        version_control_id = str(uuid.uuid4())
        version_experiment_id = str(uuid.uuid4())
        step3_url = f"{self.base_url}/api/step3"
        step3_payload = {
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3"}}}}""",
            "app": app_id,
            "draft_id": draft_id
        }
        step3_response = post_data(step3_url, json_data=step3_payload)
        if not step3_response:
            logger.error(" 第三步请求失败")
            return None

        # Step 4: 提交实验草稿
        step4_url = f"{self.base_url}/api/step4"
        step4_payload = {
            "skip_verification": False,
            "is_start": True,
            "distribute": True,
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3"}}}}""",
            "filter_rule":"[]",
            "layer_info":f"""{{"layer_id": -1,"version_resource":1}}""",
            "app": app_id,
            "draft_id": draft_id,
            "version_freeze_status":0
        }
        step4_response = post_data(step4_url, json_data=step4_payload)
        if not step4_response:
            logger.error(" 第四步请求失败")
            return None

        return step4_response

    def get_experiment_details(self, params: Dict) -> Dict:
        """获取实验详情"""
        flight_id=params["flight_id"]
        is_duplicate=params["is_duplicate"]
        url = f"{self.base_url}/datatester/api/v2/flight/view"
        params = {
            "flight_id": flight_id,
            "is_duplicate": str(is_duplicate).lower()
        }
        return fetch_data(url, params=params)

    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告"""

        app_id=params['app_id']
        flight_id=params['flight_id']
        report_type=params['report_type']
        start_ts=params['start_ts']
        end_ts=params['end_ts']
        trace_data=params['trace_data']

        url = f"{self.base_url}/datatester/api/v2/flight/view"
        params = {
            "app_id": app_id,
            "flight_id": flight_id,
            "report_type": report_type,
            "start_ts": start_ts,
            "end_ts": end_ts,
            "trace_data": trace_data
            }
        return fetch_data(url, params=params)

    def modify_experiment_status(self, params: Dict) -> Dict:
        """修改实验状态"""

        flight_id=params['flight_id'],
        action=params['action']
        if action not in ["launch", "stop"]:
            logger.error(" Invalid action. Use 'launch' or 'stop'.")

        url = f"{self.base_url}/datatester/api/v2/flight/{action}"
        payload = {"flight_id": flight_id}
        return put_data(url, json_data=payload)

    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表"""

        app_id=params['app_id'],
        keyword=params.get('keyword', ''),
        status=params.get('status', 1),
        is_required=params.get('is_required', -1),
        need_page=params.get('need_page', 1),
        page_size=params.get('page_size', 10)

        url = f"{self.base_url}/datatester/api/v2/app/{app_id}/metric/list"
        params = {
            "keyword": keyword,
            "status": status,
            "is_required": is_required,
            "need_page": need_page,
            "page_size": page_size
        }
        return fetch_data(url, params=params)

    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表"""

        app_id=params['app_id'],
        keyword=params.get('keyword', ''),
        status=params.get('status', 1),
        need_page=params.get('need_page', 1),
        page_size=params.get('page_size', 10),
        page=params.get('page', 1),
        need_default=params.get('need_default', False)

        url = f"{self.base_url}/datatester/api/v2/app/{app_id}/layer/list"
        params = {
            "keyword": keyword,
            "status": status,
            "need_page": need_page,
            "page_size": page_size,
            "page": page,
            "need_default": str(need_default).lower()
        }
        return fetch_data(url, params=params)

class V2Client(BaseClient):
    """适配config.py的V2客户端实现"""
    def __init__(self):
        super().__init__(
            base_url=config.BASE_URLS['V2'],
            auth_type='v2'
        )
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

    def list_available_metrics(self, params: Dict) -> Dict:
        return fetch_data(
            url=self._build_url('list_metrics', app_id=params['app_id']),
            params={
                "keyword": params.get('keyword', ''),
                "page": params.get('page', 1),
                "page_size": params.get('page_size', 10)
            },
            auth_type='v2'
        )

    def list_mutex_groups(self, params: Dict) -> Dict:
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

