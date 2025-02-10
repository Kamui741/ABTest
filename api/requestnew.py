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
    def __init__(self, login_url: str, session_file: str):
        self.login_url = login_url
        self.session_file = session_file

    def save_sessionid(self, sessionid: str):
        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"Session ID saved to {self.session_file}")

    def load_sessionid(self) -> Optional[str]:
        if not os.path.exists(self.session_file):
            logger.warning(f"Session ID file {self.session_file} not found,     attempting to log in.")
            return self.login()  # 直接登录并获取新的 sessionid

        try:
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"Session ID loaded from {self.session_file}")
                return sessionid
        except Exception as e:
            logger.error(f"❌ Error loading session ID file: {e}")
            return self.login()  # 读取失败时重新登录

    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """ 统一处理 HTTP 响应 """
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error(f"❌ Failed to parse JSON response from {response.url}")
            return None

        if response.status_code == 200 and response_data.get("code") == 200:
            logger.info(f"✅ Request to {response.url} succeeded")
            return response_data
        else:
            logger.error(f"❌ Request failed, status: {response.status_code}, message: {response_data.get('message', 'Unknown error')}")
            return None

    def login(self) -> Optional[str]:
        """ 登录并获取 session ID """
        try:
            response = requests.post(self.login_url, json={"email": username, "password": password})
            response_data = self._handle_response(response)
            if response_data:
                sessionid = response.cookies.get("sessionid")
                if sessionid:
                    self.save_sessionid(sessionid)
                    return sessionid
                logger.warning("Login successful but session ID not found in response cookies")
        except requests.RequestException as e:
            logger.error(f"❌ Login request failed: {e}")
        return None

    def validate_session(self, sessionid: str, test_url: str) -> bool:
        """ 验证 session ID 是否有效 """
        headers = {"Cookie": f"sessionid={sessionid}"}
        try:
            response = requests.get(test_url, headers=headers)
            return bool(self._handle_response(response))
        except requests.RequestException as e:
            logger.error(f"❌ Failed to validate session: {e}")
            return False

    def get_valid_session(self, test_url: str) -> Optional[str]:
        """ 获取有效的 session ID """
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        return self.login()

def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """ 发送 HTTP 请求 """
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
    if not sessionid:
        logger.error("❌ Failed to get a valid session")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    if json_data:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(method, url, headers=headers, data=data, json=json_data, params=params)
        return session_manager._handle_response(response)
    except requests.RequestException as e:
        logger.error(f"❌ Error occurred while making {method} request: {e}")
        return None

def fetch_data(url: str, params: Optional[Dict[str, Any]] = None):
    return send_request("GET", url, params=params)

def post_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    return send_request("POST", url, data=data, json_data=json_data)

def put_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    return send_request("PUT", url, data=data, json_data=json_data)

#######功能函数########
def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程，包含四次连续的 POST 请求。
    """

    # Step 1: 初始化实验草稿
    step1_url = "http://28.4.136.142/api/step1"
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
        logger.error("❌ 第一步请求失败")
        return None
    draft_id = step1_response.get("data",{}).get("draft_id")

    # Step 2: 配置实验指标
    step2_url = "http://28.4.136.142/api/step2"
    step2_payload = {
        "major_metric": "1545",
        "metrics": "1545",
        "app": app_id,
        "draft_id": draft_id
    }
    step2_response = post_data(step2_url, json_data=step2_payload)
    if not step2_response:
        logger.error("❌ 第二步请求失败")
        return None

    # Step 3: 配置实验版本
    version_control_id = str(uuid.uuid4())
    version_experiment_id = str(uuid.uuid4())
    step3_url = "http://28.4.136.142/api/step3"
    step3_payload = {
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
        "app": app_id,
        "draft_id": draft_id
    }
    step3_response = post_data(step3_url, json_data=step3_payload)
    if not step3_response:
        logger.error("❌ 第三步请求失败")
        return None

    # Step 4: 提交实验草稿
    step4_url = "http://28.4.136.142/api/step4"
    step4_payload = {
        "skip_verificationh": False,
        "is_start": True,
        "distribute": True,
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
        "filter_rule":"[]",
        "layer_info":f"""{{"layer_id": -1,"version_resource":1}}""",
        "app": app_id,
        "draft_id": draft_id,
        "version_freeze_status":0
    }
    step4_response = post_data(step4_url, json_data=step4_payload)
    if not step4_response:
        logger.error("❌ 第四步请求失败")
        return None

    return step4_response

def get_flight_config(flight_id: int, is_duplicate: bool = False):
    """ 获取实验配置 """
    url = f"https://28.4.136.142/datatester/api/v2/flight/view"
    params = {"flight_id": flight_id, "is_duplicate": str(is_duplicate).lower()}
    return fetch_data(url, params=params)


def get_metric_list(app_id: int, keyword: str = "", status: int = 1, is_required: int = -1, need_page: int = 1, page_size: int = 10):
    """ 获取指标列表 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/metric/list"
    params = {
        "keyword": keyword,
        "status": status,
        "is_required": is_required,
        "need_page": need_page,
        "page_size": page_size
    }
    return fetch_data(url, params=params)


def update_flight_status(flight_id: int, action: str):
    """ 修改实验状态 (启动/停止) """
    if action not in ["launch", "stop"]:
        logger.error("❌ Invalid action. Use 'launch' or 'stop'.")
        return None

    url = f"https://28.4.136.142/datatester/api/v2/flight/{action}"
    payload = {"flight_id": flight_id}
    return put_data(url, json_data=payload)


def get_experiment_report(app_id: int, flight_id: int, report_type: str, start_ts: int, end_ts: int, trace_data: str):
    """ 计算实验指标并返回指标报告 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/flight/{flight_id}/rich-metric-report"
    params = {
        "report_type": report_type,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "traceData": trace_data
    }
    return fetch_data(url, params=params)


def get_mutex_group_list(app_id: int, keyword: str = "", status: int = 1, need_page: int = 1, page_size: int = 10, page: int = 1, need_default: bool = False):
    """ 获取互斥组列表 """
    url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/layer/list"
    params = {
        "keyword": keyword,
        "status": status,
        "need_page": need_page,
        "page_size": page_size,
        "page": page,
        "need_default": str(need_default).lower()
    }
    return fetch_data(url, params=params)

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