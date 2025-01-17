'''
Author: ChZheng
Date: 2025-01-17 17:47:22
LastEditTime: 2025-01-17 17:47:23
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/requestnew.py
'''
import threading
import requests
import logging
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERNAME = "your_username"
PASSWORD = "your_password"
LOGIN_URL = "https://example.com/login"

# 辅助函数
def safe_request(method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """安全地执行 HTTP 请求"""
    try:
        return requests.request(method, url, **kwargs)
    except requests.RequestException as e:
        logger.error(f"{method.upper()} 请求异常: {e}")
    return None

def handle_response(response: requests.Response, context: str) -> Optional[Dict[str, Any]]:
    """统一处理响应"""
    try:
        response_data = response.json()
        # 如果 code != 200，认为是 session 过期
        if response_data.get("code") == 200:
            logger.info(f"{context} 成功")
            return response_data.get("data")
        else:
            logger.warning(f"{context} 业务失败，错误代码: {response_data.get('code')}, 信息: {response_data.get('message')}")
    except ValueError as e:
        logger.error(f"{context} 解析响应 JSON 失败: {e}")
    logger.error(f"{context} 请求失败，状态码: {response.status_code}, 响应: {response.text}")
    return None


def make_request(method: str, url: str, sessionid: str, **kwargs) -> Optional[Dict[str, Any]]:
    """发送带 Session ID 的 HTTP 请求"""
    headers = {"Cookie": f"sessionid={sessionid}"}
    headers.update(kwargs.pop("headers", {}))
    response = safe_request(method, url, headers=headers, **kwargs)
    if response:
        return handle_response(response, f"{method.upper()} 请求")
    return None

# Session 管理器
class SessionManager:
    """线程安全的 Session 管理器"""

    def __init__(self, login_url: str):
        self.login_url = login_url
        self._sessionid: Optional[str] = None
        self._session_lock = threading.Lock()

    def login(self) -> Optional[str]:
        """登录系统并获取 sessionid"""
        payload = {"username": USERNAME, "password": PASSWORD}
        response = safe_request("POST", self.login_url, json=payload)
        if response:
            result = handle_response(response, "登录请求")
            if result:
                sessionid = response.cookies.get("sessionid")
                if sessionid:
                    logger.info(f"登录成功，Session ID: {sessionid}")
                    return sessionid
                else:
                    logger.warning("登录成功，但未找到 Session ID")
        logger.error("登录失败，无法获取有效的 Session ID")
        return None

    def get_valid_session(self) -> Optional[str]:
        """线程安全地获取有效 Session ID"""
        with self._session_lock:
            if not self._sessionid:
                logger.info("Session ID 无效，开始重新登录")
                self._sessionid = self.login()
            return self._sessionid

    def is_session_valid(self, sessionid: str) -> bool:
        """检查当前 Session ID 是否有效"""
        try:
            # 示例验证接口，您需要根据实际接口替换 URL 和逻辑
            response = requests.get("https://example.com/session/validate", headers={"Authorization": f"Bearer {sessionid}"})
            if response.status_code == 200:
                logger.info("Session ID 验证通过")
                return True
            else:
                logger.warning(f"Session ID 验证失败，状态码: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"验证请求异常: {e}")
            return False

# 全局单例
session_manager = SessionManager(LOGIN_URL)

# 通用请求函数
def execute_request_with_session(method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """执行带 Session ID 的 HTTP 请求"""
    sessionid = session_manager.get_valid_session()
    if not sessionid:
        logger.error("无法获取有效的 Session ID")
        return None
    return make_request(method, url, sessionid=sessionid, **kwargs)

def perform_request(method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    通用请求函数，用于发送带 Session ID 的 HTTP 请求并处理结果。
    参数：
        method (str): 请求方法，例如 "GET", "POST", "PUT"。
        url (str): 请求的 URL。
        **kwargs: 其他请求参数，例如 params, data, json 等。
    返回：
        成功时返回响应的字典形式数据，失败时返回 None。
    """
    response = execute_request_with_session(method, url, **kwargs)
    if response:
        logger.info(f"{method.upper()} 请求成功，响应数据：{response}")
        return response
    else:
        logger.error(f"{method.upper()} 请求失败，URL: {url}")
        return None