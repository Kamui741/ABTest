'''
Author: ChZheng
Date: 2025-02-13 06:32:07
LastEditTime: 2025-02-13 06:32:08
LastEditors: ChZheng
Description:
FilePath: /code/ABTest/api/requestv5.py
'''
# app/config.py
import os
from pathlib import Path

class Config:
    # 认证配置
    USERNAME = os.getenv("USERNAME", "admin")
    PASSWORD = os.getenv("PASSWORD", "admin123")

    # 服务地址配置
    V1_BASE_URL = os.getenv("V1_BASE_URL", "http://28.4.136.142")
    V2_BASE_URL = os.getenv("V2_BASE_URL", "http://v2-server:8000")

    # 会话配置
    SESSION_FILE = os.getenv("SESSION_FILE", "session.txt")
    LOGIN_URL = f"{V1_BASE_URL}/api/login"  # 根据实际情况调整

    # 功能开关
    USE_V2_DIRECT = os.getenv('USE_V2_DIRECT', 'false').lower() == 'true'
    V1_ADAPTER_MODE = os.getenv('V1_ADAPTER_MODE', 'proxy')

    # 路径配置
    MAPPING_CONFIG_DIR = Path(os.getenv('MAPPING_CONFIG_DIR', 'config/v2_proxy'))

config = Config()

# app/session.py
import os
import logging
from typing import Optional, Dict, Any
import requests
from .config import config

logger = logging.getLogger("ABTestProxy")

class SessionManager:
    """统一会话管理"""
    def __init__(self):
        self.session_id = None

    def _save_session(self, session_id: str):
        """保存会话到文件"""
        try:
            with open(config.SESSION_FILE, 'w') as f:
                f.write(session_id)
            logger.info(f"Session saved to {config.SESSION_FILE}")
        except Exception as e:
            logger.error(f"Save session failed: {str(e)}")

    def _load_session(self) -> Optional[str]:
        """从文件加载会话"""
        if not os.path.exists(config.SESSION_FILE):
            return None
        try:
            with open(config.SESSION_FILE, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Load session failed: {str(e)}")
            return None

    def _validate_session(self, session_id: str) -> bool:
        """验证会话有效性"""
        test_url = f"{config.V1_BASE_URL}/api/validate"
        headers = {"Cookie": f"sessionid={session_id}"}
        try:
            response = requests.get(test_url, headers=headers)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_session(self) -> Optional[str]:
        """获取有效会话ID"""
        # 尝试加载现有会话
        if not self.session_id:
            self.session_id = self._load_session()

        # 验证现有会话
        if self.session_id and self._validate_session(self.session_id):
            return self.session_id

        # 需要重新登录
        return self.login()

    def login(self) -> Optional[str]:
        """执行登录流程"""
        try:
            response = requests.post(
                config.LOGIN_URL,
                json={"email": config.USERNAME, "password": config.PASSWORD}
            )
            if response.status_code == 200:
                self.session_id = response.cookies.get("sessionid")
                if self.session_id:
                    self._save_session(self.session_id)
                    return self.session_id
            logger.error("Login failed")
            return None
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return None

# app/clients/v1_client.py
import logging
import uuid
import requests
from typing import Optional, Dict, Any
from ..config import config
from ..session import SessionManager

logger = logging.getLogger("ABTestProxy")

class V1Client:
    def __init__(self):
        self.session = SessionManager()

    def _send_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """统一请求方法"""
        session_id = self.session.get_session()
        if not session_id:
            logger.error("No valid session")
            return None

        headers = kwargs.get('headers', {})
        headers['Cookie'] = f"sessionid={session_id}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Request failed: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            return None

    def create_experiment(self, flight_name: str, duration: int, app_id: int) -> Optional[Dict]:
        """创建实验完整流程"""
        # 各步骤URL
        step_urls = [
            f"{config.V1_BASE_URL}/api/step1",
            f"{config.V1_BASE_URL}/api/step2",
            f"{config.V1_BASE_URL}/api/step3",
            f"{config.V1_BASE_URL}/api/step4"
        ]

        # Step 1: 创建草稿
        step1_data = {
            "flight_name": flight_name,
            "duration": duration,
            "hash_strategy": "ssid",
            "app": app_id
        }
        draft_res = self._send_request('POST', step_urls[0], json=step1_data)
        if not draft_res:
            return None
        draft_id = draft_res.get('data', {}).get('draft_id')

        # Step 2-4 省略，保持原有逻辑...
        # 实际实现中需要补充完整步骤

        return draft_res  # 返回最终结果

    def get_flight_config(self, flight_id: int) -> Optional[Dict]:
        """获取实验配置"""
        url = f"{config.V1_BASE_URL}/datatester/api/v2/flight/view"
        return self._send_request('GET', url, params={'flight_id': flight_id})

    # 其他方法保持原有逻辑...

# app/proxy.py
from typing import Dict, Any
from .config import config
from .clients.v1_client import V1Client
from .mappers import FieldMapper

class ABTestProxy:
    """AB测试代理核心类"""
    def __init__(self):
        self.v1_client = V1Client()
        self.mapper = FieldMapper(config.MAPPING_CONFIG_DIR)

    def _map_request(self, api_name: str, data: Dict) -> Dict:
        """请求参数映射"""
        mapping = self.mapper.load_mapping(f"{api_name}_request")
        return self.mapper.transform(data, mapping)

    def _map_response(self, api_name: str, data: Dict) -> Dict:
        """响应参数映射"""
        mapping = self.mapper.load_mapping(f"{api_name}_response")
        return self.mapper.transform(data, mapping)

    def create_experiment(self, data: Dict) -> Dict:
        """创建实验代理"""
        if config.USE_V2_DIRECT:
            # 直连V2逻辑
            return self._call_v2_direct('/experiments', 'POST', data)

        # 走V1适配
        mapped_data = self._map_request('create_experiment', data)
        v1_response = self.v1_client.create_experiment(**mapped_data)
        return self._map_response('create_experiment', v1_response)

    def _call_v2_direct(self, endpoint: str, method: str, data: Dict) -> Dict:
        """直连V2服务"""
        url = f"{config.V2_BASE_URL}{endpoint}"
        try:
            response = requests.request(method, url, json=data)
            return response.json()
        except Exception as e:
            return {'code': 500, 'error': str(e)}

    # 其他代理方法...

# app/main.py
from fastapi import FastAPI, APIRouter
from .proxy import ABTestProxy

app = FastAPI()
router = APIRouter()
proxy = ABTestProxy()

@router.post("/experiments")
async def create_experiment(data: dict):
    return proxy.create_experiment(data)

# 其他路由...

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)