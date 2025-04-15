# auth.py
import hashlib
import hmac
import os
import time
import requests
import logging
from typing import Optional, Dict, Any

from requests import session

from config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class V1AuthProvider:
    """V1会话认证"""
    def __init__(self):
        self.login_url = config.V1_LOGIN_URL
        self.session_file = config.V1_SESSION_FILE
        self.target_url = config.V1_TARGET_URL
        self.username = config.V1_USERNAME
        self.password = config.V1_PASSWORD

    def get_auth_headers(self) -> Dict[str, str]:
        """实现AuthProvider接口"""
        sessionid = self.get_valid_session()
        return {"Cookie": f"sessionid={sessionid}"} if sessionid else {}

    def get_valid_session(self) -> Optional[str]:
        """获取 session"""
        sessionid = self._load_sessionid()
        if sessionid and self._validate_session(sessionid):
            return sessionid
        return self._login()

    def _load_sessionid(self) -> Optional[str]:
        """加载本地会话ID"""
        if not os.path.exists(self.session_file):
            logger.warning(logger.error(f"会话文件不存在: {self.session_file}")
            return self._login()
        try:
            with open(self.session_file, "r") as f:
                sessionid = f.read().strip()
                logger.info(f"加载会话ID: {sessionid}")
                return sessionid
        except Exception as e:
            logger.error(f"加载会话文件失败: {str(e)}")
            return self._login()

    def _save_sessionid(self, sessionid: str):
        """保存会话ID到文件"""

        with open(self.session_file, "w") as f:
            f.write(sessionid)
        logger.info(f"会话ID已保存至 {self.session_file}")


    def _validate_session(self, sessionid: str) -> bool:
        headers = {"Cookie":f"sessionid={sessionid}"}
        """验证会话有效性"""
        try:
            response = requests.get(
                self.target_url,
                headers=headers
            )
            return bool(self.handle_response(response))
        except requests.RequestException as e:
            logger.error(f"会话验证请求失败: {str(e)}")
            return False

    def handle_response(self, response: requests.Response) -> Optional[Dict]:
        """统一处理响应"""
        try:
            response_data = response.json()
        except requests.JSONDecodeError:
            logger.error(f"响应解析失败: {response.url}")
            return None
        if response.status_code!= 200:
            logger.error(f"请求失败,状态码 {response.status_code}")
            return None
        response_data = response.json()
        if response_data.get("code") == 200:
            logger.info("请求成功")
            return response_data
        else:
            logger.error(f"请求失败，状态码{response_data.get('code')},信息{response_data.get('message')}")
        return None

    def _login(self) -> Optional[str]:
        """执行登录流程"""
        try:
            response = requests.post(
                self.login_url,
                json={"email": self.username, "password": self.password}
            )
            response_data = self.handle_response(response)
            if response_data:
                sessionid = response.cookies.get("sessionid")
                return sessionid
            logger.warning(f"登录成功但是没找到sessionid")
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
        return None

class V2AuthProvider:
    """V2 AK/SK认证"""
    def __init__(self):
        from config import config
        self.ak = config.V2_ACCESS_KEY
        self.sk = config.V2_SECRET_KEY

    def get_headers(self):
        timestamp = str(int(time.time()))
        signature = hmac.new(
            self.sk.encode(),
            f"{timestamp}\n{self.ak}".encode(),
            hashlib.sha256
        ).hexdigest()
        return {
            "X-Access-Key": self.ak,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }