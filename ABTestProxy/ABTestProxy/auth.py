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