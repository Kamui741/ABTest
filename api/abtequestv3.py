'''
Author: ChZheng
Date: 2025-02-11 16:59:56
LastEditTime: 2025-02-13 05:53:29
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/abtequestv3.py
'''
import requests
import os
import logging
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from functools import wraps, lru_cache
from pathlib import Path

# ================== 基础配置 ==================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# ================== 服务配置 ==================
class ServiceConfig:
    V1_BASE_URL = os.getenv("V1_BASE_URL", "http://28.4.136.142")
    LOGIN_URL = f"{V1_BASE_URL}/login"
    TARGET_URL = f"{V1_BASE_URL}/healthcheck"
    SESSION_FILE = ABTestConfig.SESSION_FILE  #?
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
    session_manager = SessionManager(
        login_url=ServiceConfig.LOGIN_URL,
        session_file=ServiceConfig.SESSION_FILE
    )
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

# ================== 二期字段映射器 ==================
class SimpleFieldMapper:
    """支持默认值的简易字段映射器"""
    def __init__(self, strict_mode: bool = False, default_sep: str = "||"):
        """
        :param strict_mode: 严格模式（True=遇到错误抛出异常）
        :param default_sep: 默认值分隔符（如：field||default）
        """
        self.strict_mode = strict_mode
        self.default_sep = default_sep

    @lru_cache(maxsize=32)
    def load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self._handle_error(f"配置加载失败: {config_path}", e)
            return {}

    def transform(self, source: Dict, mapping: Dict) -> Dict:
        """执行字段映射转换"""
        result = {}
        for target_field, source_rule in mapping.items():
            try:
                # 解析路径和默认值
                path, default = self._parse_rule(source_rule)

                # 获取值
                value = self._get_value(source, path) or default

                # 设置值
                if value is not None:
                    self._set_value(result, target_field, value)

            except Exception as e:
                self._handle_error(f"处理字段 {target_field} 失败", e)

        return result

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

    def _format_error_response(self, error_msg: str) -> Dict:
        return {
            "code": 500,
            "message": f"Adapter Error: {error_msg}",
            "data": None
        }

# ================== 使用示例 ==================
if __name__ == "__main__":
    # 初始化映射器
    mapper = SimpleFieldMapper()

    # 加载配置
    config = {
        "experiment_id": "flight_id||-1",
        "experiment_name": "experiment.name||'未命名实验'",
        "owner": "creator.email||'unknown@company.com'"
    }

    # 原始数据
    source_data = {
        "flight_id": 123,
        "experiment": {
            "name": "二期实验"
        },
        "creator": {
            "user_id": "admin"
        }
    }

    # 执行转换
    result = mapper.transform(source_data, config)
    print("转换结果：")
    print(json.dumps(result, indent=2, ensure_ascii=False))