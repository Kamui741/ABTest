'''
Author: ChZheng
Date: 2025-02-12 04:41:28
LastEditTime: 2025-02-12 04:42:38
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/qushu/core/auth.py
'''
# core/auth.py
import logging
import json
from typing import Optional
import requests
from pathlib import Path
from .config import AppConfig
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class SessionManager:
    """会话生命周期管理器"""

    def __init__(self):
        self.login_url = AppConfig.V1_LOGIN_URL
        self.session_file = AppConfig.SESSION_FILE
        self.test_url = f"{AppConfig.V1_BASE_URL}/api/ping"

    def _save_session(self, session_id: str):
        """加密存储会话ID"""
        try:
            with self.session_file.open("w") as f:
                json.dump({"session_id": session_id}, f)
            logger.debug("Session saved to %s", self.session_file)
        except IOError as e:
            logger.error("Failed to save session: %s", e)

    def _load_session(self) -> Optional[str]:
        """加载存储的会话"""
        try:
            if not self.session_file.exists():
                return None
            with self.session_file.open("r") as f:
                data = json.load(f)
                return data.get("session_id")
        except (IOError, json.JSONDecodeError) as e:
            logger.warning("Load session failed: %s", e)
            return None

    def _do_login(self) -> str:
        """执行登录流程"""
        try:
            resp = requests.post(
                self.login_url,
                json={
                    "email": AppConfig.USERNAME,
                    "password": AppConfig.PASSWORD
                },
                timeout=10
            )
            resp.raise_for_status()
            session_id = resp.cookies.get("sessionid")
            if not session_id:
                raise AuthenticationError("No sessionid in response")
            return session_id
        except requests.RequestException as e:
            raise AuthenticationError(f"Login failed: {str(e)}") from e

    def validate_session(self, session_id: str) -> bool:
        """验证会话有效性"""
        try:
            resp = requests.get(
                self.test_url,
                cookies={"sessionid": session_id},
                timeout=5
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def get_session(self) -> str:
        """获取有效会话ID"""
        # 尝试加载已有会话
        if cached_id := self._load_session():
            if self.validate_session(cached_id):
                return cached_id

        # 需要重新登录
        new_session = self._do_login()
        self._save_session(new_session)
        return new_session