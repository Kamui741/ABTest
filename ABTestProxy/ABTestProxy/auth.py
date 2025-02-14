'''
Author: ChZheng
Date: 2025-02-13 14:19:26
LastEditTime: 2025-02-14 15:21:29
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/ABTestProxy/ABTestProxy/auth.py
'''

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
from .config import USERNAME, PASSWORD

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
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
            response = requests.post(self.login_url, json={"email": USERNAME, "password": PASSWORD})
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