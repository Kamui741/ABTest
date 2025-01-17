import threading
import requests
import logging
import os
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)

# 配置
LOGIN_URL = os.getenv("LOGIN_URL", "http://28.4.136.142/api/auth/login")
TARGET_URL = os.getenv("TARGET_URL", "http://28.4.136.142/api/target_endpoint")
USERNAME = os.getenv("USERNAME", "your_username")
PASSWORD = os.getenv("PASSWORD", "your_password")

class SessionManager:
    """管理 Session 的线程安全类"""
    _sessionid: Optional[str] = None
    _session_lock = threading.Lock()
    _session_updated = threading.Condition(_session_lock)

    def __init__(self, login_url: str):
        self.login_url = login_url

    def login(self) -> Optional[str]:
        """登录系统并获取 sessionid"""
        try:
            response = requests.post(self.login_url, json={"username": USERNAME, "password": PASSWORD})
            if response.status_code == 200:
                sessionid = response.cookies.get("sessionid")
                if sessionid:
                    logger.info(f"登录成功，Session ID: {sessionid}")
                    return sessionid
                else:
                    logger.warning("登录成功，但未找到 Session ID")
            else:
                logger.error(f"登录失败，状态码: {response.status_code}, 响应: {response.text}")
        except requests.RequestException as e:
            logger.error(f"登录请求异常: {e}")
        return None

    def get_valid_session(self) -> Optional[str]:
        """线程安全地获取有效 Session ID"""
        with self._session_lock:
            if self._sessionid:
                logger.info("使用缓存的 Session ID")
                return self._sessionid

            logger.info("Session ID 无效，开始重新登录")
            self._sessionid = self.login()

            if self._sessionid:
                self._session_updated.notify_all()
            return self._sessionid

def safe_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """安全地执行 HTTP 请求"""
    try:
        return requests.request(method, url, **kwargs)
    except requests.RequestException as e:
        logger.error(f"{method.upper()} 请求异常: {e}")
    return None

def make_request(method: str, url: str, sessionid: str, **kwargs) -> Optional[Dict[str, Any]]:
    """发送带 Session ID 的 HTTP 请求"""
    headers = {"Cookie": f"sessionid={sessionid}"}
    headers.update(kwargs.pop("headers", {}))
    response = safe_request(method, url, headers=headers, **kwargs)
    if response:
        if response.status_code == 401:  # Session 过期
            logger.warning("Session ID 过期")
            return None
        return handle_response(response, f"{method.upper()} 请求")
    return None

def handle_response(response: requests.Response, context: str) -> Optional[Dict[str, Any]]:
    """统一处理响应"""
    if response.status_code == 200:
        try:
            response_data = response.json()
            if response_data.get("code") == 200:
                logger.info(f"{context} 成功")
                return response_data.get("data")
            else:
                logger.warning(f"{context} 业务失败，错误代码: {response_data.get('code')}, 信息: {response_data.get('message')}")
        except ValueError as e:
            logger.error(f"{context} 解析响应 JSON 失败: {e}")
    else:
        logger.error(f"{context} 请求失败，状态码: {response.status_code}, 响应: {response.text}")
    return None

def execute_request_with_session(method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """执行带 Session ID 的 HTTP 请求"""
    session_manager = SessionManager(LOGIN_URL)
    sessionid = session_manager.get_valid_session()
    if not sessionid:
        logger.error("无法获取有效的 Session ID")
        return None
    return make_request(method, url, sessionid=sessionid, **kwargs)

def fetch_data(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """使用有效的 Session ID 获取数据"""
    return execute_request_with_session("GET", url, params=params)

def post_data_with_session(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """使用有效的 Session ID 发送 POST 请求"""
    return execute_request_with_session("POST", url, data=data, json=json_data)

def put_data_with_session(url: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """使用有效的 Session ID 发送 PUT 请求"""
    return execute_request_with_session("PUT", url, data=data, json=json_data)

def create_experiment(flight_name: str, duration: int, hash_strategy: str, app_id: int) -> Optional[Dict[str, Any]]:
    """
    创建实验的完整流程，包含四次连续的 POST 请求
    """
    try:
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
        step1_response = post_data_with_session(step1_url, json_data=step1_payload)
        if not step1_response:
            logger.error("❌ 第一步请求失败")
            return None
        draft_id = step1_response.get("draft_id")

        # Step 2: 配置实验指标
        step2_url = "http://28.4.136.142/api/step2"
        step2_payload = {
            "major_metric": "1545",
            "metrics": "1545",
            "app": app_id,
            "draft_id": draft_id
        }
        post_data_with_session(step2_url, json_data=step2_payload)

        # Step 3: 配置实验版本
        version_control_id = str(uuid.uuid4())
        version_experiment_id = str(uuid.uuid4())
        step3_url = "http://28.4.136.142/api/step3"
        step3_payload = {
            "versions": f"""[{{"type": 0, "id": "{version_control_id}", "label": "对照版本", "name":"对照版本"，"users":[],"weight":50,"config":{{"3":"3"}}}},{{"type": 1, "id": "{version_experiment_id}", "label": "实验版本", "name":"实验版本"，"users":[],"weight":50,"config":{{"3":"3}}}}""",
            "app": app_id,
            "draft_id": draft_id
        }
        post_data_with_session(step3_url, json_data=step3_payload)

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
        return post_data_with_session(step4_url, json_data=step4_payload)
    except Exception as e:
        logger.error(f"实验创建异常: {e}")
        return None


def perform_request(method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    通用请求函数，用于发送带 Session ID 的 HTTP 请求并处理结果。
    参数：
        method (str): 请求方法，例如 "GET", "POST", "PUT"。
        url (str): 请求的 URL。
        **kwargs: 其他请求参数，例如 params, data, json_data 等。
    返回：
        成功时返回响应的字典形式数据，失败时返回 None。
    """
    if method.upper() == "GET":
        response = fetch_data(url, params=kwargs.get("params"))
    elif method.upper() == "POST":
        response = post_data_with_session(url, data=kwargs.get("data"), json_data=kwargs.get("json_data"))
    elif method.upper() == "PUT":
        response = put_data_with_session(url, data=kwargs.get("data"), json_data=kwargs.get("json_data"))
    else:
        logger.error(f"不支持的请求方法: {method}")
        return None

    if response:
        logger.info(f"{method.upper()} 请求成功，响应数据：{response}")
        return response
    else:
        logger.error(f"{method.upper()} 请求失败，URL: {url}")
        return None

if __name__ == "__main__":
    # get
    url = "http://28.4.136.142/api/example_get"
    params = {"param1": "value1", "param2": "value2"}

    response = perform_request("GET", url, params=params)
    # response 已经是成功响应的字典数据（或 None），无需再手动检查。
    # post
    url = "http://28.4.136.142/api/example_post"
    json_data = {"key1": "value1", "key2": "value2"}

    response = perform_request("POST", url, json_data=json_data)
    # put
    url = "http://28.4.136.142/api/example_put"
    json_data = {"update_key": "new_value"}

    response = perform_request("PUT", url, json_data=json_data)



