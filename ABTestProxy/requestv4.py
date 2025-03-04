
# ---------------------- adapters.py ----------------------
from interfaces import IAdapter
from typing import Dict
class V1Adapter(IAdapter):
    """增强的V1协议适配器"""

    @staticmethod
    def convert_create_experiment_request(params: Dict) -> Dict:
        """V1->V2 创建实验参数转换"""
        params[hash_strategy] = "ssid"
        return params

    @staticmethod
    def convert_create_experiment_response(response: Dict) -> Dict:
        """V2->V1 创建实验响应转换"""
        return response

    @staticmethod
    def convert_get_experiment_details_request(params: Dict) -> Dict:
        """V1->V2 查询实验详情参数转换"""
        params["is_duplicate"] = False
        return params

    @staticmethod
    def convert_get_experiment_details_response(response: Dict) -> Dict:
        return response


    @staticmethod
    def convert_generate_report_request(params: Dict) -> Dict:
        """V1->V2 报告请求转换"""
        params["trace_data"] = params.get("trace_data", "")
        return params
    @staticmethod
    def convert_generate_report_response(response: Dict) -> Dict:
        """V2->V1 报告响应转换"""
        return response



    @staticmethod
    def convert_modify_experiment_status_request(params: Dict) -> Dict:
        """V1->V2 修改实验状态请求转换"""
        return {
            "flight_id": params["experiment_id"],
            "status": params["action"]
        }
    @staticmethod
    def convert_modify_experiment_status_response(response: Dict) -> Dict:
        """V2->V1 修改实验状态响应转换"""
        return response
    @staticmethod
    def convert_list_available_metrics_request(params: Dict) -> Dict:
        """V1->V2 查询可用指标请求转换"""
        return params
    @staticmethod
    def convert_list_available_metrics_response(response: Dict) -> Dict:
        """V2->V1 查询可用指标响应转换"""
        return response
    def convert_list_mutex_groups_request(params: Dict) -> Dict:
        """V1->V2 查询互斥组请求转换"""
        params["need_default"] = False
        return params
    def convert_list_mutex_groups_response(response: Dict) -> Dict:
        """V2->V1 查询互斥组响应转换"""
        return response


class V2Adapter(IAdapter):
    """V2透传适配器"""
    @staticmethod
    def convert_request(params: Dict) -> Dict:
        return params

    @staticmethod
    def convert_response(response: Dict) -> Dict:
        return response

import os
import requests
import logging
from typing import Optional, Dict, Any
from config import config
from interfaces import IAuthProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1SessionAuth(IAuthProvider):
    """V1会话认证"""
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


# ---------------------- config.py ----------------------
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
        cls.USERNAME = os.getenv("USERNAME")
        cls.PASSWORD = os.getenv("PASSWORD")

        # V2认证配置
        cls.V2_ACCESS_KEY = os.getenv("V2_ACCESS_KEY")
        cls.V2_SECRET_KEY = os.getenv("V2_SECRET_KEY")

        # 版本配置
        cls.RUNTIME_MODE = os.getenv('RUNTIME_MODE', 'V1')  # V1/V2
        cls.BASE_URLS = {
            'V1': os.getenv('V1_BASE_URL', 'https://default-v1.example.com'),
            'V2': os.getenv('V2_BASE_URL', 'https://default-v2.example.com')
        }
        cls.API_ENDPOINTS = {
            'create_experiment': {
                'V1': 'experiment/create',
                'V2': 'openapi/v2/apps/{app_id}/experiments'
            },
            'get_details': {
                'V1': 'experiment/detail',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/details'
            },
            'generate_report': {
                'V1': 'report/generate',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/metrics'
            },
            'modify_status': {
                'V1': 'experiment/status',
                'V2': 'openapi/v2/apps/{app_id}/experiments/{experiment_id}/{action}'
            },
            'list_metrics': {
                'V1': 'metrics',
                'V2': 'openapi/v2/apps/{app_id}/metrics'
            },
            'list_groups': {
                'V1': 'groups',
                'V2': 'openapi/v2/apps/{app_id}/layers'
            }
        }

    @property
    def current_base_url(self):
        return self.BASE_URLS[self.RUNTIME_MODE]

    def get_endpoint(self, name: str, **params) -> str:
        template = self.API_ENDPOINTS[name][self.RUNTIME_MODE]
        return template.format(**params)

config = ABTestConfig()


# ---------------------- factories.py ----------------------
from interfaces import IAuthProvider, IApiClient, IAdapter
from auth import V1SessionAuth, V2AKSKAuth
from v1_client import V1Client
from v2_client import V2Client
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


# api/helpers.py
import requests
import logging
import hmac
import hashlib
import time
from typing import Optional, Dict, Any, Union
from auth import SessionManager, V2AKSKAuth
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def send_request(
    method: str,
    url: str,
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    auth_type: str = 'v1'
) -> Optional[Dict]:
    """多版本兼容请求方法"""
    headers = {}

    # V1认证流程
    if auth_type == 'v1':
        session_manager = SessionManager(config.LOGIN_URL, config.SESSION_FILE)
        sessionid = session_manager.get_valid_session(config.BASE_URLS['V1'])
        headers = {"Cookie": f"sessionid={sessionid}"}

    # V2认证流程
    elif auth_type == 'v2':
        headers.update(V2AKSKAuth.get_auth_headers())

    # 智能设置Content-Type
    if json_data and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"请求失败: {e.response.status_code} {e.response.text}")
        return {"code": e.response.status_code, "message": "API请求错误"}
    except Exception as e:
        logger.error(f"请求异常: {str(e)}")
        return None

# 保持原有快捷方法（新增auth_type参数）
def fetch_data(url: str, params: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('GET', url, params=params, auth_type=auth_type)

def post_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('POST', url, json_data=json_data, auth_type=auth_type)

def put_data(url: str, json_data: Optional[Dict] = None, auth_type: str = 'v1') -> Optional[Dict]:
    return send_request('PUT', url, json_data=json_data, auth_type=auth_type)


# ---------------------- interfaces.py ----------------------
from abc import ABC, abstractmethod
from typing import Dict, Optional

class IAuthProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证头信息"""
        pass

class IApiClient(ABC):
    @abstractmethod
    def create_experiment(self, params: Dict) -> Dict:
        """创建实验（需实现参数校验）"""
        pass

    @abstractmethod
    def get_experiment_details(self, exp_id: str) -> Dict:
        """获取实验详情（需支持多种ID格式）"""
        pass

    @abstractmethod
    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告（需处理时间范围校验）"""
        pass

    @abstractmethod
    def modify_experiment_status(self, exp_id: str, action: str) -> Dict:
        """修改实验状态（需实现状态机校验）"""
        pass

    @abstractmethod
    def list_available_metrics(self, params: Dict) -> Dict:
        """获取指标列表（需支持分页）"""
        pass

    @abstractmethod
    def list_mutex_groups(self, params: Dict) -> Dict:
        """获取互斥组列表（需支持关键字过滤）"""
        pass

class IAdapter(ABC):
    @staticmethod
    @abstractmethod
    def convert_create_experiment_request(params: Dict) -> Dict:
        """转换创建实验请求参数"""
        pass

    @staticmethod
    @abstractmethod
    def convert_get_experiment_details_response(response: Dict) -> Dict:
        """转换实验详情响应格式"""
        pass

    @staticmethod
    @abstractmethod
    def convert_report_response(response: Dict) -> Dict:
        """转换实验报告响应格式"""
        pass

    @classmethod
    @abstractmethod
    def convert_metric_response(cls, response: Dict) -> Dict:
        """转换指标列表响应格式"""
        pass


# ---------------------- proxy.py ----------------------
from typing import Dict, Any
from interfaces import IApiClient, IAdapter  # 假设已有这些接口定义

class ABTestProxy:
    """增强的代理服务"""

    def __init__(self, client: IApiClient, adapter: IAdapter):
        """
        初始化代理服务
        :param client: 具体版本的客户端实例（V1Client/V2Client）
        :param adapter: 协议适配器实例
        """
        self.client = client
        self.adapter = adapter

    def create_experiment(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_create_experiment_request(params)
        raw_response = self.client.create_experiment(converted_params)
        return self.adapter.convert_create_experiment_response(raw_response)

    def get_experiment_details(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_get_experiment_details_request(params)
        raw_response = self.client.get_experiment_details(converted_params)
        return self.adapter.convert_get_experiment_details_response(raw_response)

    def generate_report(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_generate_report_request(params)
        raw_response = self.client.generate_report(converted_params)
        return self.adapter.convert_generate_report_response(raw_response)

    def modify_experiment_status(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_modify_experiment_status_request(params)
        raw_response = self.client.modify_experiment_status(converted_params)
        return self.adapter.convert_modify_experiment_status_response(raw_response)

    def list_available_metrics(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_list_available_metrics_request(params)
        raw_response = self.client.list_available_metrics(converted_params)
        return self.adapter.convert_list_available_metrics_response(raw_response)

    def list_mutex_groups(self, params: Dict) -> Dict:
        converted_params = self.adapter.convert_list_mutex_groups_request(params)
        raw_response = self.client.list_mutex_groups(converted_params)
        return self.adapter.convert_list_mutex_groups_response(raw_response)


# ---------------------- clients/v1_client.py ----------------------
from typing import Dict, Any
from interfaces import IApiClient
import uuid
import requests
import logging
from typing import Optional, Dict, Any
from helpers import post_data, put_data, fetch_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1Client(IApiClient):
    """V1客户端完整实现"""

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
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本","users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本","users":[],"weight":50,"config":{{"3":"3"}}}}""",
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

    # TODO: ip改为可配置  所有的 ip 都改为可配置
    def get_experiment_details(self, params: Dict) -> Dict:
        """获取实验详情"""
        flight_id=params["flight_id"]
        is_duplicate=params["is_duplicate"]
        url = f"https://28.4.136.142/datatester/api/v2/flight/view"
        params = {
            "flight_id": flight_id,
            "is_duplicate": str(is_duplicate).lower()
        }
        return fetch_data(url, params=params)

    def generate_report(self, params: Dict) -> Dict:
        """生成实验报告"""

        app_id=params['app_id'],
        flight_id=params['flight_id'],
        report_type=params['report_type'],
        start_ts=params['start_ts'],
        end_ts=params['end_ts'],
        trace_data=params['trace_data']

        url = f"https://28.4.136.142/datatester/api/v2/flight/view"
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

        url = f"https://28.4.136.142/datatester/api/v2/flight/{action}"
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

        url = f"https://28.4.136.142/datatester/api/v2/app/{app_id}/metric/list"
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


# clients/v2_client.py 修改URL生成逻辑
from typing import Dict, Any, Optional
from interfaces import IApiClient
from helpers import post_data, fetch_data, put_data
from config import config
# TODO: 分离功能函数
# TODO: web接口化改造
# TODO: v1v2参数化导入
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

from v1_client import V1Client
from v2_client import V2Client
from adapters import V1Adapter, V2Adapter
from auth import V1SessionAuth, V2AKSKAuth
from config import config
from proxy import ABTestProxy
import os

def main_v1():
    """V1版本调用示例"""
    # 设置环境变量（实际使用应从安全渠道获取）
    os.environ.update({
        "USERNAME": "v1_user@example.com",
        "PASSWORD": "v1_password",
        "V1_BASE_URL": "https://28.4.136.142/datatester"
    })

    # 初始化组件
    config.RUNTIME_MODE = 'V1'
    auth = V1SessionAuth()
    client = V1Client()
    adapter = V1Adapter()
    proxy = ABTestProxy(client, adapter)
    app_id = 123
    # 1. 创建实验
    create_params = {
        "name":"测试实验2022041901",
        "mode": 1,
        "endpoint_type": 1,
        "duration": 20,
        "major_metric": 29806,
        "metrics": [29806],
        "versions": [
            {
                "type": 0,
                "name": "实验组2022041901",
                "config": {"shiyu_key": "hello"}
            },
            {
                "type": 1,
                "name": "对照组2022041901",
                "config": {"shiyu_key": "world"}
            }
        ],
        "layer_info": {
            "layer_id": -1,
            "version_resource": 0.7
        }
    }


    create_res = proxy.create_experiment(create_params)
    print(f"[V1] 创建实验结果：{create_res}")
    exp_id = create_res.get('data')

    # 2. 获取实验详情
    if exp_id:
        detail_params = {
            "experiment_id": exp_id,
            "app_id": app_id
            }
        detail_res = proxy.get_experiment_details(detail_params)
        print(f"[V1] 实验详情：{detail_res}")

    # 3. 生成报告
    report_params = {
        "app_id": 123,
        "experiment_id": exp_id,
        "report_type": "daily",
        "start_ts": 1625097600,  # 2021-07-01
        "end_ts": 1627689600,     # 2021-07-31
        "fliters": []
    }
    report = proxy.generate_report(report_params)
    print(f"[V1] 实验报告：{report}")

    # 4. 修改实验状态
    status_params = {
        "experiment_id": exp_id,
        "app_id": app_id,
        "action": "launch"
    }
    status_res = proxy.modify_experiment_status(status_params)
    print(f"[V1] 修改状态结果：{status_res}")

    # 5. 获取指标列表
    metric_params = {
        "app_id": 123,
        "keyword": "关键指标",
        "need_page": 1,
        "page_size": 5,
        "page": 1
    }
    metrics = proxy.list_available_metrics(metric_params)
    print(f"[V1] 指标列表：{metrics}")

    # 6. 获取互斥组列表
    group_params = {
        "app_id": 123,
        "keyword": "互斥组",
        "need_page": 1,
        "page_size": 5,
        "page": 1
    }
    groups = proxy.list_mutex_groups(group_params)
    print(f"[V1] 互斥组列表：{groups}")



def main_v2():
    """V2版本调用示例"""
    # 设置环境变量（实际使用应从安全渠道获取）
    os.environ.update({
        "V2_ACCESS_KEY": "your_ak",
        "V2_SECRET_KEY": "your_sk",
        "V2_BASE_URL": "https://new.abtest.com/api/v2"
    })

    # 初始化组件
    config.RUNTIME_MODE = 'V2'
    auth = V2AKSKAuth()
    client = V2Client(auth)
    adapter = V2Adapter()
    proxy = ABTestProxy(client, adapter)

    # 1. 创建实验
    create_params = {
        "name": "V2优化实验",
        "mode": 1,
        "app_id": 456,
        "duration": 604800,  # 7天
        "major_metric": "metric_123",
        "metrics": ["metric_123", "metric_456"],
        "versions": [
            {
                "type": 0,
                "name": "对照组",
                "config": {"color": "blue"}
            },
            {
                "type": 1,
                "name": "实验组",
                "config": {"color": "red"}
            }
        ]
    }
    create_res = proxy.create_experiment(create_params)
    print(f"[V2] 创建实验结果：{create_res}")
    exp_id = create_res.get('data', {}).get('id')

    # 2. 获取实验详情
    if exp_id:
        detail_params = {
            "experiment_id": exp_id,}
        detail_res = proxy.get_experiment_details(detail_params)
        print(f"[V2] 实验详情：{detail_res}")

    # 3. 修改实验状态
    status_params = {
        "experiment_id": exp_id,
        "action": "launch"
    }
    status_res = proxy.modify_experiment_status(status_params)
    print(f"[V2] 修改状态结果：{status_res}")

    # 4. 获取指标列表
    metric_params = {
        "app_id": 456,
        "keyword": "留存率",
        "page": 1,
        "page_size": 10
    }
    metrics = proxy.list_available_metrics(metric_params)
    print(f"[V2] 指标列表：{metrics}")

    # 5. 获取互斥组列表
    group_params = {
        "app_id": 456,
        "keyword": "核心业务"
    }
    groups = proxy.list_mutex_groups(group_params)
    print(f"[V2] 互斥组列表：{groups}")

    # 6. 生成报告
    report_params = {
        "app_id": 456,
        "experiment_id": exp_id,
        "report_type": "overall",
        "start_ts": 1625097600,
        "end_ts": 1627689600
    }
    report = proxy.generate_report(report_params)
    print(f"[V2] 实验报告：{report}")

if __name__ == "__main__":
    print("========= V1版本调用示例 =========")
    main_v1()

    print("\n========= V2版本调用示例 =========")
    main_v2()

TODO: v1 v2 参数导入
TODO: ip 提取为公共参数
TODO: 暴露 web 接口
TODO: mock 测试
TODO: main 函数只需要一个版本