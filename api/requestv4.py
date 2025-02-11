'''
Author: ChZheng
Date: 2025-02-12 02:45:05
LastEditTime: 2025-02-12 04:51:06
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/requestv4.py
'''
import requests
import os
import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from functools import lru_cache
from pathlib import Path

# ================== 基础配置 ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ABTestProxy")
# ================== 新增全局配置 ==================
class ABTestConfig:
    USE_V2_DIRECT = False  # 全局切换开关
    V2_BASE_URL = "http://v2-server:8000"  # 二期服务地址
    V1_ADAPTER_MODE = "proxy"  # proxy | direct

# ================== 一期功能实现 ==================
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
            logger.error(f"❌ Error loading session ID file: {e}")
            return self.login()

    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """统一处理HTTP响应"""
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
            logger.error(f"❌ Login request failed: {e}")
        return None

    def validate_session(self, sessionid: str, test_url: str) -> bool:
        """验证会话ID是否有效"""
        headers = {"Cookie": f"sessionid={sessionid}"}
        try:
            response = requests.get(test_url, headers=headers)
            return bool(self._handle_response(response))
        except requests.RequestException as e:
            logger.error(f"❌ Failed to validate session: {e}")
            return False

    def get_valid_session(self, test_url: str) -> Optional[str]:
        """获取有效的会话ID"""
        sessionid = self.load_sessionid()
        if sessionid and self.validate_session(sessionid, test_url):
            return sessionid
        return self.login()

def send_request(method: str, url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
    """发送HTTP请求"""
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
    """发送GET请求"""
    return send_request("GET", url, params=params)

def post_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送POST请求"""
    return send_request("POST", url, data=data, json_data=json_data)

def put_data(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None):
    """发送PUT请求"""
    return send_request("PUT", url, data=data, json_data=json_data)


# ================== 一期功能函数 ==================
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
# ================== 字段映射处理器 ==================
class FieldMapper:
    def __init__(self):
        self.transformers = {
            'timestamp_to_iso': lambda x: datetime.fromtimestamp(x).isoformat(),
            'status_converter': self._convert_status,
            'metric_type': self._convert_metric_type
        }

    def _convert_status(self, status: int) -> str:
        status_map = {
            0: "ended",
            1: "running",
            2: "pending",
            3: "testing",
            4: "draft"
        }
        return status_map.get(status, "unknown")

    def _convert_metric_type(self, metric_type: str) -> str:
        type_map = {
            "major": "core",
            "normal": "common"
        }
        return type_map.get(metric_type, metric_type)

    @lru_cache(maxsize=32)
    def load_mapping(self, api_name: str, direction: str) -> Dict:
        """加载映射配置文件"""
        config_path = self.config_base / f"{api_name}_{direction}.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载映射配置失败: {config_path} - {str(e)}")
            raise

    def transform(self, data: Dict, mapping: Dict) -> Dict:
        """执行字段映射转换"""
        result = {}
        for target_field, rule in mapping.items():
            try:
                # 处理嵌套映射
                if 'mappings' in rule:
                    nested_data = self.transform(data, rule['mappings'])
                    result[target_field] = nested_data
                    continue

                # 解析映射规则
                source_path = rule.get('source', '')
                default_value = rule.get('default')
                transformer = self.transformers.get(rule.get('transform'))

                # 获取源数据
                value = self._get_nested_value(data, source_path.split('.'), default_value)

                # 应用转换
                if transformer and value is not None:
                    value = transformer(value)

                # 设置目标数据
                if value is not None:
                    self._set_nested_value(result, target_field.split('.'), value)

            except Exception as e:
                logger.warning(f"字段映射失败 [{target_field}]: {str(e)}")
        return result

    # 辅助方法保持不变...

    def _parse_rule(self, rule: str) -> tuple:
        """解析字段规则（支持 path||default 格式）"""
        if self.default_sep in rule:
            path, default_str = rule.split(self.default_sep, 1)
            try:
                default = json.loads(default_str)
            except json.JSONDecodeError:
                default = default_str
            return path.strip(), default
        return rule, None

    def _get_value(self, data: Dict, path: str) -> Any:
        """获取嵌套字段值（支持 . 分隔路径和数组索引）"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, list) and key.isdigit():
                current = current[int(key)] if int(key) < len(current) else None
            elif isinstance(current, dict):
                current = current.get(key)
            else:
                return None
            if current is None:
                return None
        return current

    def _set_value(self, data: Dict, path: str, value: Any):
        """设置嵌套字段值（支持 . 分隔路径）"""
        keys = path.split('.')
        current = data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

    def _handle_error(self, msg: str, error: Exception):
        """统一错误处理"""
        full_msg = f"{msg}: {str(error)}"
        if self.strict_mode:
            raise ValueError(full_msg)
        logger.warning(full_msg)
# ================== 接口代理层实现 ==================
class ABTestProxy:
    def __init__(self, v1_client, mapper: FieldMapper):
        self.v1_client = v1_client
        self.mapper = mapper
        self.api_mappings = {
            'create_experiment': {'req': 'create_experiment', 'res': 'create_experiment'},
            'get_experiment': {'req': 'get_experiment', 'res': 'get_experiment'},
            'get_report': {'req': 'get_report', 'res': 'get_report'},
            'update_status': {'req': 'update_status', 'res': 'update_status'},
            'list_metrics': {'req': 'list_metrics', 'res': 'list_metrics'},
            'list_layers': {'req': 'list_layers', 'res': 'list_layers'}
        }
        self.api_endpoints = {
            'create_experiment': '/openapi/v2/apps/{app_id}/experiments',
            'get_experiment': '/openapi/v1/apps/{app_id}/experiment/{experiment_id}/details',
            'get_report': '/openapi/v1/apps/{app_id}/experiment/{experiment_id}/metrics',
            'update_status': '/openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}/',
            'list_metrics': '/openapi/v2/apps/{app_id}/metrics',
            'list_layers': '/openapi/v2/apps/{app_id}/layers'
        }

    def create_experiment_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('create_experiment', v2_request)

    def get_experiment_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('get_experiment', v2_request)

    def get_report_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('get_report', v2_request)

    def update_status_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('update_status', v2_request)

    def list_metrics_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('list_metrics', v2_request)

    def list_layers_v2(self, v2_request: Dict) -> Dict:
        return self._process_request('list_layers', v2_request)

    def _process_request(self, api_name: str, v2_request: Dict) -> Dict:
        if ABTestConfig.USE_V2_DIRECT:
            return self._call_v2_direct(api_name, v2_request)
        return self._call_v1_proxy(api_name, v2_request)

    def _call_v1_proxy(self, api_name: str, v2_request: Dict) -> Dict:
        """原有代理逻辑"""
        try:
            mapping = self.api_mappings[api_name]
            req_map = self.mapper.load_mapping(mapping['req'], 'request')
            res_map = self.mapper.load_mapping(mapping['res'], 'response')

            v1_params = self.mapper.transform(v2_request, req_map)
            v1_response = getattr(self.v1_client, api_name)(**v1_params)

            return self._build_response(v1_response, res_map)
        except Exception as e:
            return self._error_response(str(e))

    def _call_v2_direct(self, api_name: str, params: Dict) -> Dict:
        """直连二期服务"""
        try:
            endpoint = self.api_endpoints[api_name]
            url = ABTestConfig.V2_BASE_URL + endpoint.format_map(params)

            if api_name == 'update_status':
                method = put_data
            elif api_name in ['create_experiment', 'update_status']:
                method = post_data
            else:
                method = fetch_data

            response = method(url, params=params)
            return self._format_v2_response(response)
        except Exception as e:
            return self._error_response(f"V2直连失败: {str(e)}")

    def _format_v2_response(self, raw_response: Dict) -> Dict:
        """标准化二期响应格式"""
        if raw_response and 'code' in raw_response:
            return raw_response
        return {
            "code": 500,
            "message": "Invalid V2 response format",
            "data": None
        }

    def _build_response(self, v1_response: Dict, res_map: Dict) -> Dict:
        """构建标准化响应"""
        return {
            "code": 200,
            "message": "success",
            "data": self.mapper.transform(v1_response.get('data', {}), res_map)
        }

    def _error_response(self, error_msg: str) -> Dict:
        return {
            "code": 500,
            "message": f"代理层处理错误: {error_msg}",
            "data": None
        }

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

# ================== 配置文件示例 ==================
"""
config/v2_proxy/create_experiment_request.json
{
    "mappings": {
        "flight_name": {"source": "experiment_name"},
        "duration": {"source": "duration_days"},
        "hash_strategy": {"source": "hash_type", "default": "ssid"},
        "app_id": {"source": "app_id"},
        "version_configs": {
            "source": "versions",
            "mappings": {
                "type": {"source": "version_type"},
                "name": {"source": "version_name"},
                "config": {"source": "parameters"}
            }
        }
    }
}

config/v2_proxy/create_experiment_response.json
{
    "mappings": {
        "experiment_id": {"source": "flight_id"},
        "status": {"source": "state", "transform": "status_converter"},
        "created_at": {"source": "create_time", "transform": "timestamp_to_iso"}
    }
}
"""


# ================== FastAPI路由集成 ==================
from fastapi import FastAPI, APIRouter, Body

app = FastAPI()
router = APIRouter()

@router.post("/openapi/v2/apps/{app_id}/experiments")
async def create_exp_v2(
    app_id: int,
    request_data: Dict = Body(...)
):
    return proxy_handler('create_experiment', {'app_id': app_id, **request_data})

@router.get("/openapi/v1/apps/{app_id}/experiment/{experiment_id}/details")
async def get_exp_v2(
    app_id: int,
    experiment_id: int
):
    return proxy_handler('get_experiment', {'app_id': app_id, 'experiment_id': experiment_id})

@router.get("/openapi/v1/apps/{app_id}/experiment/{experiment_id}/metrics")
async def get_report_v2(
    app_id: int,
    experiment_id: int,
    report_type: str,
    start_ts: int,
    end_ts: int,
    filters: List[str] = []
):
    params = {
        'app_id': app_id,
        'experiment_id': experiment_id,
        'report_type': report_type,
        'start_ts': start_ts,
        'end_ts': end_ts,
        'filters': filters
    }
    return proxy_handler('get_report', params)

@router.put("/openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}/")
async def update_status_v2(
    app_id: int,
    experiment_id: int,
    action: str
):
    return proxy_handler('update_status', {
        'app_id': app_id,
        'experiment_id': experiment_id,
        'action': action
    })

@router.get("/openapi/v2/apps/{app_id}/metrics")
async def list_metrics_v2(
    app_id: int,
    keyword: str = "",
    need_page: int = 1,
    page_size: int = 10,
    page: int = 1
):
    params = {
        'app_id': app_id,
        'keyword': keyword,
        'need_page': need_page,
        'page_size': page_size,
        'page': page
    }
    return proxy_handler('list_metrics', params)

@router.get("/openapi/v2/apps/{app_id}/layers")
async def list_layers_v2(
    app_id: int,
    keyword: str = "",
    need_page: int = 1,
    page_size: int = 10,
    page: int = 1
):
    params = {
        'app_id': app_id,
        'keyword': keyword,
        'need_page': need_page,
        'page_size': page_size,
        'page': page
    }
    return proxy_handler('list_layers', params)

def proxy_handler(api_name: str, params: Dict):
    """统一请求处理入口"""
    proxy = ABTestProxy(v1_client, mapper)
    return getattr(proxy, f"{api_name}_v2")(params)
# ================== 使用示例 ==================
if __name__ == "__main__":
    # 初始化组件
    session_mgr = SessionManager(login_url="...", session_file="...")
    v1_client = V1Client(session_mgr)
    mapper = FieldMapper()
    proxy = ABTestProxy(v1_client, mapper)

    # 二期创建实验请求
    v2_create_request = {
        "experiment_name": "二期实验",
        "duration_days": 30,
        "app_id": 10000305,
        "hash_type": "user_id",
        "versions": [
            {
                "version_type": 0,
                "version_name": "对照组",
                "parameters": {"feature_flag": False}
            },
            {
                "version_type": 1,
                "version_name": "实验组",
                "parameters": {"feature_flag": True}
            }
        ]
    }

    # 调用代理接口
    create_response = proxy.create_experiment_v2(v2_create_request)
    print("创建实验响应：")
    print(json.dumps(create_response, indent=2, ensure_ascii=False))

    # 二期修改状态请求
    v2_status_request = {
        "experiment_id": 12345,
        "action": "launch"
    }
    status_response = proxy.update_experiment_status_v2(v2_status_request)
    print("\n修改状态响应：")
    print(json.dumps(status_response, indent=2, ensure_ascii=False))