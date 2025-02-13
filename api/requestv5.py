'''
Author: ChZheng
Date: 2025-02-13 09:44:00
LastEditTime: 2025-02-13 17:16:37
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/requestv5.py
'''

# 代码模块化方案（按功能划分）：
# [ABTestProxy/__init__.py]
import os
from .auth import SessionManager
from .clients import ABTestProxy, V1Client
from .config import ABTestConfig, LOGIN_URL

__version__ = "1.0.0"
__all__ = [
    'SessionManager',
    'ABTestProxy',
    'V1Client',
    'ABTestConfig',
    'LOGIN_URL'
]
# # ================== 核心模块 ==================
# [ABTestProxy/auth.py]
# |- SessionManager
#    |- save_sessionid
#    |- load_sessionid
#    |- login
#    |- validate_session
#    |- get_valid_session
#    |- _handle_response
import os
import requests
import logging
from typing import Optional, Dict, Any
class SessionManager:
    """一期会话管理器"""
    def __init__(self, login_url: str, session_file: str):
        self.login_url = login_url
        self.session_file = session_file

    def save_sessionid(self, sessionid: str):
        """保存会话ID"""
        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"Session ID saved to {self.session_file}")

    def load_sessionid(self) -> Optional[str]:
        """加载会话ID"""
        if not os.path.exists(self.session_file):
            logger.warning(f"Session ID file {self.session_file} not found, attempting to log in.")
            return self.login()
        try:
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"Session ID loaded from {self.session_file}")
                return sessionid
        except Exception as e:
            logger.error(f" Error loading session ID file: {e}")
            return self.login()

    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """统一处理HTTP响应"""
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error(f" Failed to parse JSON response from {response.url}")
            return None

        if response.status_code == 200 and response_data.get("code") == 200:
            logger.info(f" Request to {response.url} succeeded")
            return response_data
        else:
            logger.error(f" Request failed, status: {response.status_code}, message: {response_data.get('message', 'Unknown error')}")
            return None

    def login(self) -> Optional[str]:
        """登录并获取会话ID"""
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
            logger.error(f" Login request failed: {e}")
        return None

    def validate_session(self, sessionid: str, test_url: str) -> bool:
        """验证会话ID是否有效"""
        headers = {"Cookie": f"sessionid={sessionid}"}
        try:
            response = requests.get(test_url, headers=headers)
            return bool(self._handle_response(response))
        except requests.RequestException as e:
            logger.error(f" Failed to validate session: {e}")
            return False

    def get_valid_session(self, test_url: str) -> Optional[str]:
        """获取有效的会话ID"""
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        return self.login()

# [ABTestProxy/mappers.py]
# |- FieldMapper
#    |- load_mapping
#    |- transform
#    |- _get_nested_value
#    |- _set_nested_value
import json
import logging
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Any
class FieldMapper:
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path)
        self.default_sep = "||"

    @lru_cache(maxsize=32)
    def load_mapping(self, api_name: str, direction: str) -> Dict:
        """加载简化的映射配置"""
        config_file = self.config_path / f"{api_name}_{direction}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载映射配置失败: {config_file} - {str(e)}")
            return {}

    def transform(self, data: Dict, mapping: Dict) -> Dict:
        """执行简化版字段映射"""
        result = {}
        for target_field, source_path in mapping.items():
            try:
                # 支持默认值语法：field.path||default_value
                if self.default_sep in source_path:
                    path, default_str = source_path.split(self.default_sep, 1)
                    default = json.loads(default_str)
                else:
                    path = source_path
                    default = None

                # 获取嵌套值
                value = self._get_nested_value(data, path.split('.'), default)

                # 设置到目标字段
                if value is not None:
                    self._set_nested_value(result, target_field.split('.'), value)

            except Exception as e:
                logger.warning(f"字段映射失败 [{target_field} <- {source_path}]: {str(e)}")
        return result

    def _get_nested_value(self, data: Dict, path: List[str], default: Any = None) -> Any:
        """获取嵌套字段值"""
        current = data
        for key in path:
            if isinstance(current, dict):
                current = current.get(key, default)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if index < len(current) else default
            else:
                return default
            if current is None:
                return default
        return current

    def _set_nested_value(self, data: Dict, path: List[str], value: Any):
        """设置嵌套字段值"""
        current = data
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value

# # ================== 客户端模块 ==================
# [ABTestProxy/clients/__init__.py]
from .proxy import ABTestProxy
from .v1_client import V1Client

__all__ = ['ABTestProxy', 'V1Client']
# |- ABTestProxy
#    |- _create_proxy_method
class ABTestProxy:
    # 显式声明V2到V1的映射关系（Key: V2接口名, Value: V1方法名）
    _API_MAPPINGS = {
        'create_experiment': 'create_experiment',
        'get_experiment_details': 'get_flight_config',
        'generate_report': 'get_experiment_report',
        'modify_experiment_status': 'update_flight_status',
        'list_available_metrics': 'get_metric_list',
        'list_mutex_groups': 'get_mutex_group_list'
    }

    def __init__(self, v1_client, mapper: FieldMapper):
        self.v1_client = v1_client
        self.mapper = mapper

        # 动态注册所有接口方法
        for v2_method, v1_method in self._API_MAPPINGS.items():
            setattr(self, v2_method, self._create_proxy_method(v1_method))

    def _create_proxy_method(self, v1_method_name: str):
        """创建代理方法工厂"""
        def proxy_method(v2_request: Dict) -> Dict:
            try:
                # 加载字段映射配置（使用V2方法名）
                req_map = self.mapper.load_mapping(v2_method_name, 'request')
                res_map = self.mapper.load_mapping(v2_method_name, 'response')

                # 转换请求参数
                v1_params = self.mapper.transform(v2_request, req_map)

                # 调用V1方法
                v1_response = getattr(self.v1_client, v1_method_name)(**v1_params)

                # 转换响应结果
                return {
                    "code": 200,
                    "message": "success",
                    "data": self.mapper.transform(v1_response.get('data', {}), res_map)
                }
            except Exception as e:
                return {
                    "code": 500,
                    "message": f"代理处理错误: {str(e)}",
                    "data": None
                }

        # 获取当前V2方法名（通过闭包捕获）
        v2_method_name = inspect.currentframe().f_back.f_locals['v2_method']
        proxy_method.__name__ = v2_method_name
        return proxy_method
# [ABTestProxy/clients/v1_client.py]
# |- V1Client
#    |- create_experiment
#    |- get_experiment
#    |- get_report
#    |- update_status
#    |- list_metrics
#    |- list_layers
from typing import Dict
from ..auth import SessionManager
from ..api.core import (
    create_experiment,
    get_flight_config,
    get_experiment_report,
    update_flight_status,
    get_metric_list,
    get_mutex_group_list
)

class V1Client:
    def __init__(self, session_manager: SessionManager):
        self.session = session_manager

    def create_experiment(self, **params) -> Dict:
        return create_experiment(
            flight_name=params['flight_name'],
            duration=params['duration'],
            hash_strategy=params.get('hash_strategy', 'ssid'),
            app_id=params['app_id']
        )

    def get_experiment(self, **params) -> Dict:
        return get_flight_config(
            flight_id=params['flight_id'],
            is_duplicate=params.get('is_duplicate', False)
        )

    def get_report(self, **params) -> Dict:
        return get_experiment_report(
            app_id=params['app_id'],
            flight_id=params['flight_id'],
            report_type=params['report_type'],
            start_ts=params['start_ts'],
            end_ts=params['end_ts'],
            trace_data=params.get('trace_data', '')
        )

    def update_status(self, **params) -> Dict:
        return update_flight_status(
            flight_id=params['flight_id'],
            action=params['action']
        )

    def list_metrics(self, **params) -> Dict:
        return get_metric_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            is_required=params.get('is_required', -1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10)
        )

    def list_layers(self, **params) -> Dict:
        return get_mutex_group_list(
            app_id=params['app_id'],
            keyword=params.get('keyword', ''),
            status=params.get('status', 1),
            need_page=params.get('need_page', 1),
            page_size=params.get('page_size', 10),
            page=params.get('page', 1),
            need_default=params.get('need_default', False)
        )
# # ================== 接口实现模块 ==================
# [ABTestProxy/api/__init__.py]
from .core import *
from .helpers import *
__all__ = [
    'create_experiment',
    'get_flight_config',
    'get_metric_list',
    'update_flight_status',
    'get_experiment_report',
    'get_mutex_group_list',
    'send_request',
    'fetch_data',
    'post_data',
    'put_data'
]
# [ABTestProxy/api/core.py]
# |- create_experiment
# |- get_flight_config
# |- get_metric_list
# |- update_flight_status
# |- get_experiment_report
# |- get_mutex_group_list
import uuid
import requests
import logging
from typing import Optional, Dict, Any
from .helpers import post_data, put_data, fetch_data
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

# [ABTestProxy/api/helpers.py]
# |- send_request
# |- fetch_data
# |- post_data
# |- put_data
import requests
from typing import Optional, Dict, Any
from ..auth import SessionManager
def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """发送HTTP请求"""
    session_manager = SessionManager(login_url, session_file)
    sessionid = session_manager.get_valid_session(target_url)
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

# # ================== 配置模块 ==================
# [ABTestProxy/config.py]
# |- ABTestConfig
# |- LOGIN_URL
# |- TARGET_URLS
import os
class ABTestConfig:
    SESSION_FILE = os.getenv('SESSION_FILE', 'session.txt')

# 认证信息从环境变量获取
username = os.getenv("USERNAME", "admin")
password = os.getenv("PASSWORD", "admin123")
LOGIN_URL = os.getenv('LOGIN_URL', 'https://28.4.136.142/api/login')