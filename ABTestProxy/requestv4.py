
# # ================== 接口实现模块 ==================
# [ABTestProxy/api/core.py]
import uuid
import requests
import logging
from typing import Optional, Dict, Any
from api.helpers import post_data, put_data, fetch_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程,包含四次连续的 POST 请求。
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
        logger.error(" 第一步请求失败")
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
        logger.error(" 第二步请求失败")
        return None

    # Step 3: 配置实验版本
    version_control_id = str(uuid.uuid4())
    version_experiment_id = str(uuid.uuid4())
    step3_url = "http://28.4.136.142/api/step3"
    step3_payload = {
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3}}}}""",
        "app": app_id,
        "draft_id": draft_id
    }
    step3_response = post_data(step3_url, json_data=step3_payload)
    if not step3_response:
        logger.error(" 第三步请求失败")
        return None

    # Step 4: 提交实验草稿
    step4_url = "http://28.4.136.142/api/step4"
    step4_payload = {
        "skip_verification": False,
        "is_start": True,
        "distribute": True,
        "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3}}}}""",
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
        logger.error(" Invalid action. Use 'launch' or 'stop'.")
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
# api/helper.py

import requests
from typing import Optional, Dict, Any
from auth import SessionManager
from config import LOGIN_URL,SESSION_FILE,TARGET_URL
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """发送HTTP请求"""
    session_manager = SessionManager(LOGIN_URL, SESSION_FILE)
    sessionid = session_manager.get_valid_session(TARGET_URL)
    if not sessionid:
        logger.error(" Failed to get a valid session")
        return None

    headers = {"Cookie": f"sessionid={sessionid}"}
    if json_data:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(method, url, headers=headers, data=data, json=json_data, params=params)
        return session_manager._handle_response(response)
    except requests.RequestException as e:
        logger.error(f" Error occurred while making {method} request: {e}")
        return None

def fetch_data(url: str, params: Optional[Dict[str, Any]] = None):
    """发送GET请求"""
    return send_request("GET", url, params=params)

def post_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送POST请求"""
    return send_request("POST", url, data=data, json_data=json_data)

def put_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送PUT请求"""
    return send_request("PUT", url, data=data, json_data=json_data)

# clients/v1_clients.py
# ---------------------- clients/v1_client.py ----------------------
from typing import Dict, Any
from interfaces import IApiClient
from api.core import (
    create_experiment,
    get_flight_config,
    get_experiment_report,
    update_flight_status,
    get_metric_list,
    get_mutex_group_list
)

class V1Client(IApiClient):
    """V1客户端完整实现"""

    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（参数需适配V1格式）"""
        return create_experiment(
            flight_name=params['flight_name'],
            duration=params['duration'],
            hash_strategy=params.get('hash_strategy', 'ssid'),
            app_id=params['app_id']
        )

    def get_experiment_details(self, exp_id: str) -> Dict:
        """获取实验详情"""
        return get_flight_config(
            flight_id=exp_id,
            is_duplicate=False
        )

    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告"""
        return get_experiment_report(
            app_id=params['app_id'],
            flight_id=params['flight_id'],
            report_type=params['report_type'],
            start_ts=params['start_ts'],
            end_ts=params['end_ts'],
            trace_data=params.get('trace_data', '')
        )

    def modify_experiment_status(self, exp_id: str, action: str) -> Dict:
        """修改实验状态"""
        return update_flight_status(
            flight_id=exp_id,
            action=action
        )

    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表"""
        return get_metric_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            is_required=params.get('is_required', -1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10)
        )

    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表"""
        return get_mutex_group_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10),
            page=params.get('page', 1),
            need_default=params.get('need_default', False)
        )

    # 保持与IApiClient接口兼容
    def get_experiment_details(self, exp_id: str) -> Dict:
        """接口兼容实现（参数适配在Adapter处理）"""
        return super().get_experiment_details(exp_id)
# clients/v2_clients.py
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
# adapters.py

class V1Adapter(IAdapter):
    """增强的V1协议适配器"""

    @staticmethod
    def convert_create_request(params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        return {
            "app_id": params["app_id"],
            "name": params["flight_name"],  # 字段名转换
            "mode": 1,  # 固定值
            "endpoint_type": params.get("endpoint_type", 1),
            "duration": params["duration"],
            "major_metric": params["major_metric"],
            "metrics": params["metrics"],
            "versions": [{
                "type": v["type"],
                "name": v["name"],
                "config": v["config"]
            } for v in params["versions"]],
            "layer_info": params.get("layer_info")
        }

    @staticmethod
    def convert_create_response(response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return {
            "code": response.get("code", 200),
            "message": response.get("message", "success"),
            "data": response.get("data")  # 直接返回V2的实验ID
        }

    @staticmethod
    def convert_detail_response(response: Dict) -> Dict:
        """V2->V1 详情响应转换"""
        v2_data = response.get("data", {})
        return {
            "id": v2_data.get("id"),
            "name": v2_data.get("name"),
            "status": v2_data.get("status"),
            "versions": [{
                "id": v["id"],
                "name": v["name"],
                "type": v["type"]
            } for v in v2_data.get("versions", [])]
        }

    @staticmethod
    def convert_report_response(response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        v2_data = response.get("data", {})
        return {
            "calculation_results": v2_data.get("calculation_results", {}),
            "metrics": [{
                "id": m["id"],
                "name": m["name"]
            } for m in v2_data.get("metrics", [])]
        }

class V2Adapter(IAdapter):
    """V2透传适配器"""
    @staticmethod
    def convert_request(params: Dict) -> Dict:
        return params

    @staticmethod
    def convert_response(response: Dict) -> Dict:
        return response
# auth.py
import os
import requests
import logging
from typing import Optional, Dict, Any
from config import config
from interfaces import IAuthProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1SessionAuth(IAuthProvider):
    """V1会话认证（完整实现原有SessionManager功能）"""
    def __init__(self):
        self.login_url = config.V1_LOGIN_URL
        self.session_file = config.V1_SESSION_FILE
        self.target_url = config.V1_TARGET_URL
        self.username = config.V1_USERNAME
        self.password = config.V1_PASSWORD
        self._sessionid: Optional[str] = None

    def get_auth_headers(self) -> Dict[str, str]:
        """实现IAuthProvider接口"""
        sessionid = self.get_valid_session()
        return {"Cookie": f"sessionid={sessionid}"} if sessionid else {}

    def get_valid_session(self) -> Optional[str]:
        """整合原有SessionManager的核心逻辑"""
        sessionid = self._load_sessionid()
        if sessionid and self._validate_session(sessionid):
            return sessionid
        return self._login()

    def _load_sessionid(self) -> Optional[str]:
        """加载本地会话ID"""
        if not os.path.exists(self.session_file):
            return None
        try:
            with open(self.session_file, "r") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"加载会话文件失败: {str(e)}")
            return None

    def _save_sessionid(self, sessionid: str):
        """保存会话ID到文件"""
        try:
            with open(self.session_file, "w") as f:
                f.write(sessionid)
            logger.info(f"会话ID已保存至 {self.session_file}")
        except Exception as e:
            logger.error(f"会话ID保存失败: {str(e)}")

    def _validate_session(self, sessionid: str) -> bool:
        """验证会话有效性"""
        try:
            response = requests.get(
                self.target_url,
                headers={"Cookie": f"sessionid={sessionid}"},
                timeout=5
            )
            return self._handle_response(response) is not None
        except requests.RequestException as e:
            logger.error(f"会话验证请求失败: {str(e)}")
            return False

    def _handle_response(self, response: requests.Response) -> Optional[Dict]:
        """统一处理响应"""
        try:
            data = response.json()
            if response.status_code == 200 and data.get("code") == 200:
                return data
            logger.error(f"请求失败: {data.get('message', '未知错误')}")
            return None
        except Exception as e:
            logger.error(f"响应解析失败: {str(e)}")
            return None

    def _login(self) -> Optional[str]:
        """执行登录流程"""
        try:
            response = requests.post(
                self.login_url,
                json={"email": self.username, "password": self.password},
                timeout=10
            )
            data = self._handle_response(response)

            if data and (sessionid := response.cookies.get("sessionid")):
                self._save_sessionid(sessionid)
                self._sessionid = sessionid
                logger.info("登录成功，获取到有效会话ID")
                return sessionid

            logger.warning("登录成功但未获取到会话ID")
            return None
        except requests.RequestException as e:
            logger.error(f"登录请求失败: {str(e)}")
            return None

class V2AKSKAuth(IAuthProvider):
    """V2 AK/SK认证"""
    def get_auth_headers(self) -> Dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        signature = hmac.new(
            config.V2_SECRET_KEY.encode(),
            f"{timestamp}\n{config.V2_ACCESS_KEY}".encode(),
            hashlib.sha256
        ).hexdigest()
        return {
            "X-Access-Key": config.V2_ACCESS_KEY,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }

# config.py

import os

class ABTestConfig:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._reload()
        return cls._instance

    @classmethod
    def _reload(cls):
        # 基础配置
        cls.SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')
        cls.LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')
        cls.USERNAME = os.getenv("USERNAME", "admin")
        cls.PASSWORD = os.getenv("PASSWORD", "admin123")

        # V2认证配置
        cls.V2_ACCESS_KEY = os.getenv("V2_ACCESS_KEY")
        cls.V2_SECRET_KEY = os.getenv("V2_SECRET_KEY")

        # 版本配置
        cls.RUNTIME_MODE = os.getenv('RUNTIME_MODE', 'V1')  # V1/V2
        cls.BASE_URLS = {
            'V1': 'https://28.4.136.142/datatester/api/v1',
            'V2': 'https://28.4.136.142/datatester/api/v2'
        }
        cls.API_ENDPOINTS = {
            'create_experiment': {
                'V1': 'experiment/create',
                'V2': 'experiments'
            },
            'get_details': {
                'V1': 'experiment/detail',
                'V2': 'experiments/{id}'
            },
            'generate_report': {
                'V1': 'report/generate',
                'V2': 'reports'
            },
            'modify_status': {
                'V1': 'experiment/status',
                'V2': 'experiments/{id}/status'
            },
            'list_metrics': {
                'V1': 'metrics',
                'V2': 'metrics'
            },
            'list_groups': {
                'V1': 'groups',
                'V2': 'mutex-groups'
            }
        }

    @property
    def current_base_url(self):
        return self.BASE_URLS[self.RUNTIME_MODE]

    def get_endpoint(self, name: str, **params) -> str:
        template = self.API_ENDPOINTS[name][self.RUNTIME_MODE]
        return template.format(**params)

config = ABTestConfig()
# factories.py

from interfaces import IAuthProvider, IApiClient, IAdapter
from auth import V1SessionAuth, V2AKSKAuth
from clients import V1Client, V2Client
from adapters import V1Adapter, V2Adapter
from config import config

class AuthFactory:
    @staticmethod
    def create() -> IAuthProvider:
        if config.RUNTIME_MODE == 'V1':
            return V1SessionAuth()
        return V2AKSKAuth()

class ClientFactory:
    @staticmethod
    def create(auth: IAuthProvider) -> IApiClient:
        if config.RUNTIME_MODE == 'V1':
            return V1Client()
        return V2Client(auth)

class AdapterFactory:
    @staticmethod
    def create() -> IAdapter:
        if config.RUNTIME_MODE == 'V1':
            return V1Adapter()
        return V2Adapter()
# interfaces.py

from abc import ABC, abstractmethod
from typing import Dict

class IAuthProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        pass

class IApiClient(ABC):
    @abstractmethod
    def create_experiment(self, params: Dict) -> Dict:
        pass

    @abstractmethod
    def get_experiment_details(self, exp_id: str) -> Dict:
        pass

class IAdapter(ABC):
    @staticmethod
    @abstractmethod
    def convert_request(params: Dict) -> Dict:
        pass

    @staticmethod
    @abstractmethod
    def convert_response(response: Dict) -> Dict:
        pass
# proxy.py

class ABTestProxy:
    """增强的代理服务"""

    def create_experiment(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_create_request(params)
        raw_response = self.client.create_experiment(converted_params)
        return self.adapter.convert_create_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        exp_id = params["experiment_id"]
        raw_response = self.client.get_experiment_details(exp_id)
        return self.adapter.convert_detail_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        converted_params = {
            "app_id": params["app_id"],
            "experiment_id": params["experiment_id"],
            "report_type": params["report_type"],
            "start_ts": params["start_ts"],
            "end_ts": params["end_ts"]
        }
        raw_response = self.client.generate_report(converted_params)
        return self.adapter.convert_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        return self.client.modify_experiment_status(
            params["experiment_id"],
            params["action"]
        )

    def list_available_metrics(self, params: Dict) -> Dict:
        raw_response = self.client.list_available_metrics(params)
        return {
            "metrics": [{
                "id": m["id"],
                "name": m["name"]
            } for m in raw_response.get("data", {}).get("metrics", [])]
        }

    def list_mutex_groups(self, params: Dict) -> Dict:
        raw_response = self.client.list_mutex_groups(params)
        return {
            "groups": [{
                "id": g["id"],
                "name": g["name"]
            } for g in raw_response.get("data", [])]
        }
# main.py
from proxy import ABTestProxy

# 初始化代理（自动根据配置选择版本）
proxy = ABTestProxy()

# 创建实验（自动转换协议）
response = proxy.create_experiment({
    "name": "新用户引导实验",
    "app_id": 1001,
    "duration": 30
})

# 获取实验详情
details = proxy.get_experiment_details(response["data"]["experiment_id"])